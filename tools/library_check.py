"""Bagimsiz kutuphane (scipy) kontrolu — G*Power KANITI DEGILDIR, uygulama kodu DEGILDIR.
Oturum 1 (inceleme) sirasinda GUI vektorlerini capraz kontrol etmek icin kullanildi.
Kullanim: python -I tools/library_check.py oracle/gpower_vectors.csv"""
import csv, math, sys
from scipy import stats, optimize

def power(dz, n, alpha, tails):
    d = abs(dz); df = n - 1; nc = d * math.sqrt(n)
    tc = stats.t.ppf(1 - alpha / tails, df)
    up = stats.nct.sf(tc, df, nc)
    lo = 0.0
    if tails == 2:
        lo = stats.nct.cdf(-tc, df, nc)
        if math.isnan(lo):          # H-11: alt kuyruk NaN -> ~0
            lo = 0.0
    return up + lo, tc, df, nc

def apriori(dz, alpha, target, tails):
    f = lambda x: power(dz, x, alpha, tails)[0] - target
    if f(2) >= 0:
        return 2
    hi = 100.0
    while f(hi) < 0:
        hi *= 1.6
    x = optimize.brentq(f, 2, hi, xtol=1e-10, maxiter=300)
    return max(math.ceil(math.floor(x * 1e10 + 0.5) / 1e10), 2)

def main(path):
    ok = tot = 0
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['status'] != 'GUI-TOPLANDI':
            continue
        t, dz, a = int(r['tails']), float(r['dz']), float(r['alpha'])
        if r['mode'] == 'a-priori':
            n = apriori(dz, a, float(r['power']), t)
            n_ok = str(n) == r['gp_n_total']
        else:
            n = math.floor(float(r['n_input']) + 0.5); n_ok = True
        p, tc, df, nc = power(dz, n, a, t); s = -1 if dz < 0 else 1
        got = (f'{p:.7f}', f'{s*tc:.7f}', str(df), f'{s*nc:.7f}')
        exp = (r['gp_actual_power'], r['gp_critical_t'], r['gp_df'], r['gp_ncp'])
        tot += 1; good = n_ok and got == exp; ok += good
        if not good:
            print('FARK', r['id'], n, got, exp)
    print(f'{ok}/{tot} vektor 7 basamaga kadar ayni')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'oracle/gpower_vectors.csv')
