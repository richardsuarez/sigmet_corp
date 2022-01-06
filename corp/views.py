import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from corp.auxiliar_functions import *
from corp.models import *


def principal(request):
    if request.POST:
        username = request.POST['user']
        password = request.POST['password']

        user = authenticate(request=None, username=username, password=password)
        if user is not None:
            login(request, user)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print('except2')
            print('username: \'' + username + '\'')
            print('pass: \'' + password + '\'')
            content = {
                'invalid_login': True,
                'msg': 'Usuario no válido'
            }
            return render(request, 'corp/principal.html', content)
        else:
            if check_password(password, user.password):
                return HttpResponseRedirect(reverse('corp:index'))
            else:
                print('else')
                content = {
                    'invalid_login': True,
                    'msg': 'Contraseña incorrecta'
                }
                return render(request, 'corp/principal.html', content)
    return render(request, 'corp/principal.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('corp:principal'))


def cant_inst(request):
    return render(request, 'corp/index.html')


def generalidades_instrumento(request):
    instr_single = remove_duplicated_instruments()
    magns = Magnitudes.objects.all()
    cant_instr = 0
    lista1, lista2, lista3, lista4 = obtener_instrumento_fabricante(instr_single)
    cant_inst_multifunc_elect_uso = 0
    cant_inst_multifunc_elect_almacenado = 0
    cant_inst_multifunc_nom_dif_uso = 0
    cant_inst_multifunc_nom_dif_almacenado = 0
    cant_uso = 0
    cant_roto = 0
    cant_alm = 0
    for ins in instr_single:
        cant_instr += 1
        for m in magns:
            if m.grpmagnom.grpmagnom == 'Electricidad' and ins.idmag_id == m.idmag and ins.magiddb_id == m.magiddb:
                if ins.instdescripcion == 'Multifunción con 2 o 3 magnitudes eléctricas':
                    if ins.estadoinstnom.estadoinstnom == 'Uso':
                        cant_inst_multifunc_elect_uso += 1
                    else:
                        if ins.estadoinstnom.estadoinstnom == 'Almacenado':
                            cant_inst_multifunc_elect_almacenado += 1
                break
        if ins.instdescripcion == 'Multifunción con 2 o 3 nomenclaturas diferentes':
            if ins.estadoinstnom.estadoinstnom == 'Uso':
                cant_inst_multifunc_nom_dif_uso += 1
            else:
                if ins.estadoinstnom.estadoinstnom == 'Almacenado':
                    cant_inst_multifunc_nom_dif_almacenado += 1
        if ins.estadoinstnom.estadoinstnom == 'Uso':
            cant_uso += 1
        else:
            if ins.estadoinstnom.estadoinstnom == 'Almacenado':
                cant_alm += 1
            else:
                if ins.estadoinstnom.estadoinstnom == 'Roto':
                    cant_roto += 1

    return render(request, 'corp/generalidades/gen.html', {'cantidad_instrumentos': cant_instr,
                                                           'cant_inst_multifunc_elect_uso': cant_inst_multifunc_elect_uso,
                                                           'cant_inst_multifunc_elect_almacenado': cant_inst_multifunc_elect_almacenado,
                                                           'cant_inst_multifunc_nom_dif_uso': cant_inst_multifunc_nom_dif_uso,
                                                           'cant_inst_multifunc_nom_dif_almacenado': cant_inst_multifunc_nom_dif_almacenado,
                                                           'lista1': lista1,
                                                           'lista2': lista2,
                                                           'lista3': lista3,
                                                           'lista4': lista4,
                                                           'inst_uso': cant_uso,
                                                           'inst_roto': cant_roto,
                                                           'inst_alm': cant_alm,
                                                           })


def magnitud_instrumento(request):
    inst_per_magn_per_group = instrumentos_por_magnitud()

    return render(request, 'corp/magnitud/magn.html', {'ipmpg': inst_per_magn_per_group,
                                                       })


def instrumentos_indicacion_data(request):
    instr_single = remove_duplicated_instruments()
    cant_instr_an = 0
    cant_instr_dig = 0
    cant_inst_no_ind_visual = 0
    for ins in instr_single:
        if ins.instindvisual == 'Analógico':
            cant_instr_an += 1
        else:
            if ins.instindvisual == 'Digital':
                cant_instr_dig += 1
            else:
                if ins.instindvisual is None:
                    cant_inst_no_ind_visual += 1
    instr_ind_visual = [('Digital', cant_instr_dig), ('Analógico', cant_instr_an),
                        ('Sin indicador visual', cant_inst_no_ind_visual)]
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Cantidad de instrumentos por indicador visual'},
        'xAxis': {
            'categories': [x[0] for x in instr_ind_visual],
            'crosshair': 'true'
        },
        'credits': {'enabled': 'false'},
        'series': [{
            'name': 'Cantidad',
            'data': [x[1] for x in instr_ind_visual]
        }]
    }

    return JsonResponse(chart)


def instrumentos_trabajo_gen(request):
    instr_single = remove_duplicated_instruments()
    magns = Magnitudes.objects.all()

    inst_tension_subset = []
    instr_micrometro = []
    instrumentos_grupo_presion = []
    instr_trab = []
    count_vacuometro = 0
    count_pie_rey = 0
    count_pie_rey_profundidad = 0
    count_micrometro = 0
    count_mag_frec = 0
    cant_cintas = 0
    cant_medidor_nivel = 0
    cant_medidor_angulo = 0
    cant_comparador_caratula = 0
    cant_regla = 0
    cant_galga = 0
    cant_ttr = 0
    cant_armonico = 0
    cant_multif = 0
    cant_trab = 0
    cant_presion = 0

    for ins in instr_single:
        if ins.catusonom.catusonom == 'Trabajo':
            cant_trab += 1
            instr_trab.append(ins)
            if ins.instnom.__contains__('Voltimetro') or ins.instnom.__contains__('Voltímetro'):
                inst_tension_subset.append(ins)
            if ins.instnom.__contains__('Vacuómetro') or ins.instnom.__contains__('Vacuometro'):
                count_vacuometro += 1
            if ins.instnom.__contains__('Pie de rey') or ins.instnom.__contains__('pie de rey'):
                count_pie_rey += 1
                for m in magns:
                    if m.magnom == 'Profundidad':
                        if ins.idmag_id == m.idmag and ins.magiddb_id == m.magiddb:
                            count_pie_rey_profundidad += 1
                            break
            if ins.instnom.__contains__('Micrómetro'):
                instr_micrometro.append(ins)
                count_micrometro += 1
            if ins.instnom.__contains__('Cinta métrica'):
                cant_cintas += 1
            if ins.instnom.__contains__('Medidor de nivel'):
                cant_medidor_nivel += 1
            if ins.instnom.__contains__('Medidor de ángulo'):
                cant_medidor_angulo += 1
            if ins.instnom.__contains__('Comparador de carátulas'):
                cant_comparador_caratula += 1
            if ins.instnom.__contains__('Regla'):
                cant_regla += 1
            if ins.instnom.__contains__('Galga'):
                cant_galga += 1
            if ins.instnom.__contains__('TTR') or ins.instnom.__contains__('Medidor de Relación de Transformación'):
                cant_ttr += 1
            if ins.instnom.__contains__('Medidor de armónico'):
                cant_armonico += 1
            if ins.instdescripcion is not None:
                if ins.instdescripcion.__contains__('Multifunción'):
                    cant_multif += 1
            for m in magns:
                if m.magnom == 'Frecuencia':
                    if m.idmag == ins.idmag_id and m.magiddb == ins.magiddb_id:
                        count_mag_frec += 1
                else:
                    if m.grpmagnom.grpmagnom == 'Presión':
                        if m.idmag == ins.idmag_id and m.magiddb == ins.magiddb_id:
                            instrumentos_grupo_presion.append(ins)
                            cant_presion += 1

    miliohm_lista, ohm_lista, kiloohm_lista, megaohm_lista = instrumentos_medidores_resistencia(instr_trab)

    # Obtener instrumentos de tensión existentes por niveles 1kV-5kV
    count_1_kV = obtener_instrumentos_rango(-1000000, 1, 'kV', inst_tension_subset)

    count_1_5_kV = obtener_instrumentos_rango(1, 5, 'kV', inst_tension_subset)

    # Obtener instrumentos de tensión existentes por niveles 5.1kV-10kV
    count_5_10_kV = obtener_instrumentos_rango(5.1, 10, 'kV', inst_tension_subset)

    # Obtener instrumentos de tensión existentes por niveles 10.1kV-15kV
    count_10_15_kV = obtener_instrumentos_rango(10.1, 15, 'kV', inst_tension_subset)

    # Obtener instrumentos de tensión existentes por niveles 15.1kV-150kV
    count_15_150_kV = obtener_instrumentos_rango(15.1, 150, 'kV', inst_tension_subset)

    # Obtener instrumentos de tensión existentes por niveles 150.1kV-300kV
    count_150_300_kV = obtener_instrumentos_rango(15.1, 300, 'kV', inst_tension_subset)

    # Obtener instrumentos de tensión existentes por niveles mas de 300kV
    count_301_kV = obtener_instrumentos_rango(300, 1000000, 'kV', inst_tension_subset)

    # Obtener instrumentos del grupo de magnitudes presion en el rango de 0Pa a 50Pa
    count_0_50_Pa = obtener_instrumentos_rango(0, 50, 'Pa', instrumentos_grupo_presion)

    # Obtener instrumentos del grupo de magnitudes presion en el rango de 1.1kPa a 7KPa
    count_1_7_kPa = obtener_instrumentos_rango(1, 7, 'kPa', instrumentos_grupo_presion)

    # Obtener instrumentos del grupo de magnitudes presion en el rango de 7.1kPa a 10kPa
    count_7_10_kPa = obtener_instrumentos_rango(7.1, 10, 'kPa', instrumentos_grupo_presion)

    # Obtener instrumentos del grupo de magnitudes presion en el rango de 10.1kPa a 20kPa
    count_10_20_kPa = obtener_instrumentos_rango(10.1, 20, 'kPa', instrumentos_grupo_presion)

    # Obtener instrumentos del grupo de magnitudes presion en el rango de 20.1kPa a 25kPa
    count_20_25_kPa = obtener_instrumentos_rango(20.1, 25, 'kPa', instrumentos_grupo_presion)

    # Obtener instrumentos con nombre micrometro en el rango hasta 100mm
    count_micrometro_100_mm = obtener_instrumentos_rango(-1000000, 100, 'mm', instr_micrometro)

    # Obtener instrumentos con nombre micrometro en el rango entre  100mm y 500mm
    count_micrometro_100_500_mm = obtener_instrumentos_rango(100.1, 500, 'mm', instr_micrometro)

    # Obtener instrumentos con nombre micrometro en el rango entre  100mm y 500mm
    count_micrometro_500_1000_mm = obtener_instrumentos_rango(500.1, 1000, 'mm', instr_micrometro)

    # Obtener instrumentos con nombre micrometro en el rango entre  100mm y 500mm
    count_micrometro_1000_mm = obtener_instrumentos_rango(1000.1, 1000000, 'mm', instr_micrometro)

    dictionary = cantidad_inst_por_grupo(instr_trab, magns)

    return render(request, 'corp/rng/rango.html',
                  {'cant_trab': cant_trab,
                   'count_1_kV': count_1_kV,
                   'count_1_5_V': count_1_5_kV,
                   'count_5_10_kV': count_5_10_kV,
                   'count_10_15_kV': count_10_15_kV,
                   'count_15_150_kV': count_15_150_kV,
                   'count_150_300_kV': count_150_300_kV,
                   'count_301_kV': count_301_kV,
                   'count_mag_frec': count_mag_frec,
                   'count_vacuometro': count_vacuometro,
                   'count_0_50_Pa': count_0_50_Pa,
                   'count_1_7_kPa': count_1_7_kPa,
                   'count_7_10_kPa': count_7_10_kPa,
                   'count_10_20_kPa': count_10_20_kPa,
                   'count_20_25_kPa': count_20_25_kPa,
                   'count_pie_rey': count_pie_rey,
                   'count_pie_rey_profundidad': count_pie_rey_profundidad,
                   'count_micrometro': count_micrometro,
                   'count_micrometro_100_mm': count_micrometro_100_mm,
                   'count_micrometro_100_500_mm': count_micrometro_100_500_mm,
                   'count_micrometro_500_1000_mm': count_micrometro_500_1000_mm,
                   'count_micrometro_1000_mm': count_micrometro_1000_mm,
                   'count_cintas': cant_cintas,
                   'count_medidor_nivel': cant_medidor_nivel,
                   'count_medidor_angulo': cant_medidor_angulo,
                   'count_comparador_caratula': cant_comparador_caratula,
                   'count_regla': cant_regla,
                   'count_galga': cant_galga,
                   'count_ttr': cant_ttr,
                   'count_arm': cant_armonico,
                   'count_multif': cant_multif,
                   'count_trab': cant_trab,
                   'cant_electr': dictionary.get('cant_elect'),
                   'cant_presion': cant_presion,
                   'cant_temp': dictionary.get('cant_temp'),
                   'cant_flujo': dictionary.get('cant_flujo'),
                   'cant_volumen': dictionary.get('cant_volumen'),
                   'cant_dim': dictionary.get('cant_dim'),
                   'cant_masa': dictionary.get('cant_masa'),
                   'cant_fuerza': dictionary.get('cant_fuerza'),
                   'cant_fis_quim': dictionary.get('cant_fis_quim'),
                   'cant_vibr': dictionary.get('cant_vibr'),
                   'cant_ruido': dictionary.get('cant_ruido'),
                   'cant_ilum': dictionary.get('cant_ilum'),
                   'miliohm': miliohm_lista,
                   'ohm': ohm_lista,
                   'kiloohm': kiloohm_lista,
                   'megaohm': megaohm_lista,
                   })


def instrumentos_trabajo_pc(request):
    instr_single = remove_duplicated_instruments()
    inst_trab = []
    for i in instr_single:
        if i.catusonom.catusonom == 'Trabajo':
            inst_trab.append(i)

    # Determinar instrumentos por procesos corporativos

    instruments_per_companies_per_provinces = instrumentos_procesos_corporativos(inst_trab)

    return render(request, 'corp/rng/instr_trab_proc_corp.html', {'ipcpp': instruments_per_companies_per_provinces})


def instrumentos_trabajo_explot(request):
    instr_single = remove_duplicated_instruments()
    inst_trab = []
    for i in instr_single:
        if i.catusonom.catusonom == 'Trabajo':
            inst_trab.append(i)

    # Determinar instrumentos por años de explotacion

    inst_per_comp_0_10, inst_per_comp_10_20, inst_per_comp_20 = instrumentos_anhos_explotacion(inst_trab)

    return render(request, 'corp/rng/instr_trab_explot.html', {'ipcpp_0_10': inst_per_comp_0_10,
                                                               'ipcpp_10_20': inst_per_comp_10_20,
                                                               'ipcpp_20': inst_per_comp_20})


def instrumentos_trabajo_fabr(request):
    instr_single = remove_duplicated_instruments()
    inst_trab = []
    for i in instr_single:
        if i.catusonom.catusonom == 'Trabajo':
            inst_trab.append(i)

    # Determinar instrumentos por fabricante

    list1, list2, list3, list4 = obtener_instrumento_fabricante(inst_trab)

    return render(request, 'corp/rng/instr_trab_fabr.html', {'fab1': list1,
                                                             'fab2': list2,
                                                             'fab3': list3,
                                                             'fab4': list4})


def patrones(request):
    instrumentos = Instrumentos.objects.all()

    # Determinar cantidad de instrumentos que sean patrones

    instr_single = remove_duplicated_instruments()
    instr_patr = []
    cant_patr = 0
    for isin in instr_single:
        if isin.catusonom.catusonom == 'Patrón':
            instr_patr.append(isin)
            cant_patr += 1

    # Determinar la cantidad de instrumentos patrones de energia monofasicos
    cant_energia_monofasico = 0
    cad = "Patrón de energía monofásicos de alta exactitud"
    cad1 = "Patrón de energía monofasicos de alta exactitud"
    cad2 = "Patrón de energia monofásicos de alta exactitud"
    cad3 = "Patrón de energia monofasicos de alta exactitud"
    for ip in instr_patr:
        desc = str(ip.instdescripcion).lower()
        if desc == cad.lower() or desc == cad1.lower() or desc == cad2.lower() or desc == cad3.lower():
            cant_energia_monofasico += 1

    # Determinar la cantidad de instrumentos patrones de energia trifasicos
    cant_energia_trifasico = 0
    cad = "Patrón de energía trifásicos de alta exactitud"
    cad1 = "Patrón de energía trifasicos de alta exactitud"
    cad2 = "Patrón de energia trifásicos de alta exactitud"
    cad3 = "Patrón de energia trifasicos de alta exactitud"
    for ip in instr_patr:
        desc = str(ip.instdescripcion).lower()
        if desc == cad.lower() or desc == cad1.lower() or desc == cad2.lower() or desc == cad3.lower():
            cant_energia_trifasico += 1

    # Determinar la cantidad de instrumentos patrones de energia de trabajo
    cant_patr_ener_trab = 0
    cad1 = 'Patrón de energia de trabajo'
    cad2 = 'Patrón de energía de trabajo'
    for ip in instr_patr:
        if str(ip.instdescripcion).lower() == cad1.lower() or str(ip.instdescripcion).lower() == cad2.lower():
            cant_patr_ener_trab += 1

    # Determinar la cantidad de instrumentos patrones de trabajo

    # Determinar cantidad de patrones de electricidad
    magnitudes = Magnitudes.objects.all()

    dictionary = cantidad_inst_por_grupo(instr_patr, magnitudes)

    instr_patr_elect = dictionary.get('instr_patr_elect')
    instr_patr_pres = dictionary.get('instr_patr_pres')
    instr_patr_temp = dictionary.get('instr_patr_temp')

    cant_electr_intensidad, cant_electr_tension, cant_electr_resistencia = cantidad_patrones_por_magnitud(
        instr_patr_elect, magnitudes)

    # Determinar cantidad de patrones de relacion de Transformacion
    cant_rel_trans = 0
    cad = "Medidor de Relación de Transformación"
    cad1 = "TTR"
    for ip in instr_patr:
        if str(ip.instdescripcion).lower() == cad.lower() or str(ip.instdescripcion).lower() == cad1.lower():
            cant_rel_trans += 1

    # Determinar cantidad de patrones de presion hasta 1MPa
    cant_presion_1mpa = obtener_instrumentos_rango(-1000000, 1, 'MPa', instr_patr_pres)

    # Determinar cantidad de patrones de presion hasta 1.1MPa a 10MPa
    cant_presion_1_10 = obtener_instrumentos_rango(1.1, 10, 'MPa', instr_patr_pres)

    # Determinar cantidad de patrones de presion hasta 10.1MPa a 100MPa
    cant_presion_10_100 = obtener_instrumentos_rango(10.1, 100, 'MPa', instr_patr_pres)

    # Determinar cantidad de patrones de presion hasta 100.1MPa a 250MPa
    cant_presion_100_250 = obtener_instrumentos_rango(100.1, 250, 'MPa', instr_patr_pres)

    # Determinar cantidad de patrones de temperatura hasta 100 grados
    cant_temp_100 = obtener_instrumentos_rango(-1000000, 100, 'ºC', instr_patr_temp)

    # Determinar cantidad de patrones de temperatura de 100 grados a 500grados
    cant_temp_100_500 = obtener_instrumentos_rango(100.1, 500, 'ºC', instr_patr_temp)

    # Determinar cantidad de patrones de temperatura de 500grados a 1000grados
    cant_temp_500_1000 = obtener_instrumentos_rango(500.1, 1000, 'ºC', instr_patr_temp)

    # Determinar cantidad de patrones de temperatura de 1000grados a 2000grados
    cant_temp_1000_2000 = obtener_instrumentos_rango(1000.1, 2000, 'ºC', instr_patr_temp)

    # Determinar cantidad de patrones de ensayos metalograficos
    cant_patr_metalograficos = 0
    cad = "Patrón de ensayos metalográficos"
    cad1 = "Patrón de ensayos metalograficos"
    for ip in instr_patr:
        if str(ip.instdescripcion).lower() == cad.lower() or str(ip.instdescripcion).lower() == cad1.lower():
            cant_patr_metalograficos += 1

    # Determinar cantidad de patrones de ensayos quimicos
    cant_patr_quimicos = 0
    cad = "Patrón de ensayos químicos"
    cad1 = "Patrón de ensayos quimicos"
    for ip in instr_patr:
        if str(ip.instdescripcion).lower() == cad.lower() or str(ip.instdescripcion).lower() == cad1.lower():
            cant_patr_quimicos += 1

    return render(request, 'corp/patron/patron.html', {'cant_patr': cant_patr,
                                                       'cant_energia_monofasico': cant_energia_monofasico,
                                                       'cant_energia_trifasico': cant_energia_trifasico,
                                                       'cant_patr_ener_trab': cant_patr_ener_trab,
                                                       'cant_electr': dictionary.get('cant_elect'),
                                                       'cant_electr_intensidad': cant_electr_intensidad,
                                                       'cant_electr_tension': cant_electr_tension,
                                                       'cant_electr_resistencia': cant_electr_resistencia,
                                                       'cant_rel_trans': cant_rel_trans,
                                                       'cant_presion': dictionary.get('cant_presion'),
                                                       'cant_presion_1mpa': cant_presion_1mpa,
                                                       'cant_presion_1_10': cant_presion_1_10,
                                                       'cant_presion_10_100': cant_presion_10_100,
                                                       'cant_presion_100_250': cant_presion_100_250,
                                                       'cant_temp': dictionary.get('cant_temp'),
                                                       'cant_temp_100': cant_temp_100,
                                                       'cant_temp_100_500': cant_temp_100_500,
                                                       'cant_temp_500_1000': cant_temp_500_1000,
                                                       'cant_temp_1000_2000': cant_temp_1000_2000,
                                                       'cant_patr_dimensional': dictionary.get('cant_dim'),
                                                       'cant_patr_dureza': dictionary.get('cant_dureza'),
                                                       'cant_patr_metalografico': cant_patr_metalograficos,
                                                       'cant_patr_quimicos': cant_patr_quimicos,
                                                       'cant_flujo': dictionary.get('cant_flujo'),
                                                       'cant_volumen': dictionary.get('cant_volumen'),
                                                       'cant_masa': dictionary.get('cant_masa'),
                                                       'cant_fuerza': dictionary.get('cant_fuerza'),
                                                       'cant_fis_quim': dictionary.get('cant_fis_quim'),
                                                       'cant_vibr': dictionary.get('cant_vibr'),
                                                       'cant_ruido': dictionary.get('cant_ruido'),
                                                       'cant_ilum': dictionary.get('cant_ilum'),
                                                       })


# Data Grafico para cantidad de instrumentos por magnitud
def instrumento_magnitud_data(request):
    instr_por_mag = []
    for i in Magnitudes.objects.all():
        instr_por_mag.append((i.magnom, Instrumentos.objects.filter(idmag=i).count()))

    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Cantidad de Instrumentos por Magnitudes'},
        'backgroundColor': '#162447',
        'plotOptions': {
            'bar': {
                'stacking': 'normal'
            }},
        'credits': {'enabled': 'false'},
        'series': [{
            'name': 'Cantidad',
            'data': [{'name': x[0], 'y': x[1]} for x in instr_por_mag]
        }]
    }

    return JsonResponse(chart)


def informe_magnitudes(request):
    export_informe_magnitudes()

    filename = 'Informe Instrumentos.xlsx'
    # Define the full file path
    file_path = 'static/docs/' + filename
    # Open the file for reading content

    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
