import datetime as dt


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        #if (start_date + dt.timedelta(n)).weekday == 6:
        #    yield start_date + dt.timedelta(n+1)
        #else:
        yield start_date + dt.timedelta(n)


def get_slots(hours, rdvs, duree_rdv):
    duration = dt.timedelta(minutes=duree_rdv)
    slots = sorted([(hours[0], hours[0])] + rdvs + [(hours[1], hours[1])])
    free_slots = []
    #print('RDV', rdvs)
    for start, end in ((slots[i][1], slots[i + 1][0]) for i in range(len(slots) - 1)):
        while start + duration <= end:
            #("{:%H:%M} - {:%H:%M}".format(start, start + duration))
            free_slots.append(start)
            start += duration
    return free_slots


def horaires_ouvert_mat(d, params):
    wd = d.weekday() + 1
    if wd == 1:
        return [dt.datetime.combine(d, params.h_deb_mat_lundi), dt.datetime.combine(d, params.h_fin_mat_lundi)]
    if wd == 2:
        return [dt.datetime.combine(d, params.h_deb_mat_mardi), dt.datetime.combine(d, params.h_fin_mat_mardi)]
    if wd == 3:
        return [dt.datetime.combine(d, params.h_deb_mat_mercredi), dt.datetime.combine(d, params.h_fin_mat_mercredi)]
    if wd == 4:
        return [dt.datetime.combine(d, params.h_deb_mat_jeudi), dt.datetime.combine(d, params.h_fin_mat_jeudi)]
    if wd == 5:
        return [dt.datetime.combine(d, params.h_deb_mat_vendredi), dt.datetime.combine(d, params.h_fin_mat_vendredi)]
    if wd == 6:
        return [dt.datetime.combine(d, params.h_deb_mat_samedi), dt.datetime.combine(d, params.h_fin_mat_samedi)]
    if wd == 7:
        return [dt.datetime.combine(d, dt.time(hour=0, minute=0)), dt.datetime.combine(d, dt.time(hour=0, minute=0))]


def horaires_ouvert_am(d, params):
    wd = d.weekday() + 1
    if wd == 1:
        return [dt.datetime.combine(d, params.h_deb_am_lundi), dt.datetime.combine(d, params.h_fin_am_lundi)]
    if wd == 2:
        return [dt.datetime.combine(d, params.h_deb_am_mardi), dt.datetime.combine(d, params.h_fin_am_mardi)]
    if wd == 3:
        return [dt.datetime.combine(d, params.h_deb_am_mercredi), dt.datetime.combine(d, params.h_fin_am_mercredi)]
    if wd == 4:
        return [dt.datetime.combine(d, params.h_deb_am_jeudi), dt.datetime.combine(d, params.h_fin_am_jeudi)]
    if wd == 5:
        return [dt.datetime.combine(d, params.h_deb_am_vendredi), dt.datetime.combine(d, params.h_fin_am_vendredi)]
    if wd == 6:
        return [dt.datetime.combine(d, params.h_deb_am_samedi), dt.datetime.combine(d, params.h_fin_am_samedi)]
    if wd == 7:
        return [dt.datetime.combine(d, dt.time(hour=0, minute=0)), dt.datetime.combine(d, dt.time(hour=0, minute=0))]


def ouvertures_par_jour(debut, fin, params):
    out = []
    for d in daterange(debut, fin):
        #print(d.strftime("%Y-%m-%d"))
        #print(horaires_ouvert_mat(d, params))
        out.append(horaires_ouvert_mat(d, params))
        out.append(horaires_ouvert_am(d, params))
    return out
