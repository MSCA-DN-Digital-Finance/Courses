"""
00_prepare_data.py
------------------------------------------------------------------
Course: Spatial and Spatio-Temporal Anomaly Detection
Lab 0 - Data preparation

Reads the Romanian ATU (UAT/LAU2) shapefile and the vaccination /
COVID-19 incidence / socio-economic table, joins them on SIRUTA,
simplifies the geometry (the raw .shp is ~72 MB) and writes a
course GeoPackage used by all later labs.

Usage:
    python 00_prepare_data.py --shp ../data/ro_atu.shp \
                              --csv ../data/ro_vaccines.csv \
                              --out ../data/ro_course.gpkg
"""
import argparse
import geopandas as gpd
import pandas as pd

# short, code-friendly names for the variables used in the course
RENAME = {
    "Maximum Covid 19 Incidence Rate 3rd Wave": "inc_w3",
    "Covid 19 Incidence Rate 20.10.2021": "inc_w4",
    "Vaccination Rate 26.05.2021": "vac_may",
    "Vaccination Rate 05.10.2021": "vac_oct",
    "Vaccination Dose 1 26.05.2021": "dose1_may",
    "Vaccination Dose 1 05.10.2021": "dose1_oct",
    "population": "pop",
    "County": "county",
    "Administrative Territorial Unit": "atu",
    "Elderly (65+) 2020 (%)": "elderly",
    "Relative poverty 2016 (%)": "poverty",
    "Lower secondary education (8 grades) 2011 (%)": "low_edu",
    "People pe sqkm 2018": "density",
    "Family doctors 1000 inhabitants": "doctors",
    "Neoprotestants from Population 2011 (%)": "neoprot",
    "Roma proportion": "roma",
    "Migration experience": "migration",
    "Votes cast for \"YES\" at the referendum 2018 (%)": "ref_yes",
    "Living space per person 2020 (sqm)": "living",
    "Distances on roads (average in km to all cities in Romania)": "remote",
    "Core city (dummy)": "core_city",
    "Periurban locality (dummy)": "periurban",
}


def main(shp, csv, out, tol):
    gdf = gpd.read_file(shp)
    df = pd.read_csv(csv)
    df = df.rename(columns=RENAME)
    gdf["siruta"] = gdf["siruta"].astype(int)
    df["siruta"] = df["siruta"].astype(int)

    m = gdf.merge(df, on="siruta", how="inner", validate="1:1")
    print(f"shapefile: {len(gdf)} units | table: {len(df)} rows | joined: {len(m)}")

    # Queen contiguity on the ORIGINAL (unsimplified) borders, saved as GAL so
    # that Python (libpysal) and R (spdep::read.gal) use identical neighbours
    from libpysal.weights import Queen
    w = Queen.from_dataframe(m, ids=m["siruta"].tolist(), use_index=False)
    print(f"Queen weights: mean neighbours = {w.mean_neighbors:.2f}, islands = {len(w.islands)}")
    gal = out.replace(".gpkg", "_queen.gal")
    with open(gal, "w") as f:
        f.write(f"0 {w.n} siruta queen\n")
        for i in m["siruta"]:
            nb = w.neighbors[i]
            f.write(f"{i} {len(nb)}\n{' '.join(map(str, nb))}\n")
    print(f"written {gal}")

    # topology-preserving simplification: keeps shared borders consistent
    # enough for contiguity weights (we also use a snapping tolerance later)
    m["geometry"] = m.geometry.simplify(tol, preserve_topology=True)

    # derived variables
    m["vac_change"] = m["vac_oct"] - m["vac_may"]          # p.p. gained May->Oct
    m["inc_change"] = m["inc_w4"] - m["inc_w3"]           # wave 4 minus wave 3
    # approximate case counts (incidence is per 1,000 inhabitants)
    m["cases_w3"] = (m["inc_w3"] * m["pop"] / 1000).round().astype(int)
    m["cases_w4"] = (m["inc_w4"] * m["pop"] / 1000).round().astype(int)

    m.to_file(out, layer="atu", driver="GPKG")
    print(f"written {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shp", default="../data/ro_atu.shp")
    ap.add_argument("--csv", default="../data/ro_vaccines.csv")
    ap.add_argument("--out", default="../data/ro_course.gpkg")
    ap.add_argument("--tol", type=float, default=150.0, help="simplify tolerance (m)")
    a = ap.parse_args()
    main(a.shp, a.csv, a.out, a.tol)
