
from sqlalchemy import text

query_grades = text("""
        SELECT trr.TR_ID AS TR_ID,
               orr.PRZ_NAZWA AS NAZWA,
               orr.OC_PKT AS PUNKTY
        FROM TRYBRR trr
        LEFT JOIN OCENARR orr ON orr.TR_ID = trr.TR_ID
        WHERE orr.PRZ_NAZWA NOT LIKE '%rozmowa kw.%'
          AND orr.PRZ_NAZWA NOT LIKE '%Ocena dyplom%'
          AND orr.PRZ_NAZWA NOT LIKE '%sprawdzian predyspozycji%'
          AND orr.OC_PKT != -1
          AND orr.OC_PKT != 0
          AND EXTRACT(YEAR FROM trr.TR_ZMIANA) IN ({years_placeholder})
        ORDER BY trr.TR_ID
        """)

query_courses = text("""
        SELECT DISTINCT
        wy.WD_NAZWA              AS WD_NAZWA,
        ki.KK_ID                 AS KK_ID,
        ki.KK_NAZWA              AS KK_NAZWA
        FROM KIERUNEK ki
        LEFT JOIN WYDZIAL wy ON wy.WD_ID = ki.WD_ID
        WHERE KK_NAZWA IS NOT NULL AND KK_OPIS_WWW IS NOT NULL
        AND KK_NAZWA NOT LIKE '%test%' AND KK_NAZWA NOT LIKE '%XX%'
        ORDER BY KK_NAZWA
        """)

query_personal = text("""
        SELECT DISTINCT
            trr.TR_ID AS TR_ID,
            trr.TR_TRYBRR AS TRYB,
            trr.TR_ZMIANA AS TR_ZMIANA,
            CASE alb.AL_PNAKIERIND
                WHEN 'olimpijczyk' THEN 1
                ELSE 0
            END AS CZY_OLIMPIJCZYK,
            alb.AL_PNAKIERPRIO AS PRIORYTET_KIERUNKU,
            alb.AL_PWROKSEM AS ROK_SEMESTR,
            alb.AL_PROFILKLASY AS PROFIL_KLASY,
            NVL(szk.SZ_SKROT, 'brak') AS SZKOLA_SKROT,
            szk.SZ_MIASTO AS SZKOLA_MIASTO,
            adr.ADR_WIES AS ADRES_WIES_MIASTO,
            adr.ADR_WOJEWODZTWO AS ADR_WOJEWODZTWO,
            osk.OK_SUMAPKT AS PUNKTY,
            ki.KK_ID AS KK_ID
        FROM TRYBRR trr
        LEFT JOIN ALBUM alb ON alb.AL_ID = trr.AL_ID
        LEFT JOIN CZLOWIEK czl ON czl.CZ_ID = trr.CZ_ID
        LEFT JOIN ADRES adr ON czl.CZ_ID = adr.CZ_ID
        LEFT JOIN OSOBAKIERUNEK osk ON osk.TR_ID = trr.TR_ID
        LEFT JOIN OSOBAWYDZIAL osw ON osw.TR_ID = trr.TR_ID
        LEFT JOIN SZKOLA szk ON szk.SZ_ID = alb.SZ_ID
        LEFT JOIN KIERUNEK ki ON ki.KK_ID = osk.KK_ID
        WHERE alb.AL_PNAKIERINDOPIS IS NULL
          AND ki.KK_NAZWA IS NOT NULL
          AND adr.ADR_WIES IS NOT NULL
          AND adr.ADR_WOJEWODZTWO IS NOT NULL
          AND osk.OK_SUMAPKT > 0
          AND EXTRACT(YEAR FROM trr.TR_ZMIANA) IN ({years_placeholder})
        ORDER BY trr.TR_ID
        """)