# -*- coding: utf-8 -*-

"""
columntype -- type of the column; format of table: "ID (length): description"
    0x00 (2): Dummy
    0x01 (2): Temperature [°C]
    0x02 (2): Radiation [W]
    0x07 (2): Storage [kWh]
    0x08 (2): Date
    0x09 (2): Time [min]
    0x0A (1): Output
    0x0B (2): Function active (Controller)
    0x0C (2): Function active (status automatic/manual)
    0x0D (2): Error Temperature
    0x0E (2): Error Output
    0x0F (2): Storage [h]
    0x10 (2): Seconds
    0x13 (2): Flowrate [l/min]
    0x1B (2?): Tapping [l/min/10]
    (0xFE: used for local timestamp)
    (0xFF : Unknown entry, length given in arg)
"""

prozeda_systems = { 
    'SungoSXL_1221_de' : [
        [0x08, 'd', 'Datum'],
        [0x09, 'm', 'Zeit'],
        [0x01, 't0', 'T1 Kollektor'],
        [0x01, 't1', 'T2 Speicher 1- unten'],
        [0x01, 't2', 'T3 Speicher  oben'],
        [0x01, 't3', 'T4 T', True],
        [0x01, 't4', 'T5 Speicher 2- unten'],
        [0x01, 't5', 'T6 Ertrag   T'],
        [0x01, 't6', 'T7 Rückl.Anh. T'],
        [0x01, 't7', 'T8 Rückl.Anh. T'],
        [0x01, 't8', 'T9 T', True],
        [0x00, 'i1', 'Dummy 1', True],
        [0x02, 'r', 'Strahlung'],
        [0x00, 'i2', 'Dummy 2', True],
        [0x00, 'i3', 'Dummy 3', True],
        [0x0A, 'o0', 'Solarpumpe'],
        [0x0A, 'o1', 'Ventil'],
        [0x0A, 'o2', 'Holzvergaser'],
        [0x0A, 'o3', 'Ausgang 4', True],
        [0x0A, 'o4', 'Ausgang 5', True],
        [0x0A, 'o5', 'Ausgang 6', True],
        [0x0D, 'e0', 'Fehler Temperatur 1'],
        [0x0D, 'e1', 'Fehler Temperatur 2'],
        [0x0E, 'e2', 'Fehler Ausgang'],
        [0x07, 'h0', 'Ertrag Speicher 1'],
        [0x07, 'h1', 'Ertrag Speicher 2'],
        [0xFF, 'i4', 'Dummy 4', True, 2],
        [0x0F, 'r0', 'Laufzeit Speicher 1'],
        [0x0F, 'r1', 'Laufzeit Speicher 2'],
        [0xFF, 'i5', 'Dummy 5', True, 2],
        [0x0B, 'f0', 'Funktion aktiv (Regelstatus)'],
        [0x0C, 'f1', 'Funktion aktiv (Status Automatik/Hand)'],
        [0x13, 'v0', 'Volumenstrom'],
        [0x00, 'i6', 'Dummy 6', True],
        [0x00, 'i7', 'Dummy 7', True],
    ],
    'SungoSXLplus_1221_de' : [
        [0x08, 'd', 'Datum'],
        [0x09, 'm', 'Uhrzeit'],
        [0x10, 's', 'Sekunden'],
        [0x01, 't0', 'T1 Kollektor 1'],
        [0x01, 't1', 'T2 Speicher 1- unten'],
        [0x01, 't2', 'T3 T', True],
        [0x01, 't3', 'T4 T', True],
        [0x01, 't4', 'T5 Speicher 2-unten'],
        [0x01, 't5', 'T6 ErtragRL'],
        [0x01, 't6', 'T7 Speicher 2-oben'],
        [0x01, 't7', 'T8 Heizkreis RL'],
        [0x01, 't8', 'T9 T', True],
        [0x1B, 'v0', 'Volumenstrom'],
        [0x1B, 'v1', 'VFS_Q'],
        [0x01, 'v2', 'VSF_T'],
        [0x0A, 'o0', 'Solarpumpe'],
        [0x0A, 'o1', 'Ventil Sp 1/2'],
        [0x0A, 'o2', 'Thermostat A'],
        [0x0A, 'o3', 'Thermostat B'],
        [0x0A, 'o4', 'Freier Regler'],
        [0x0A, 'o5', 'Rücklaufanh.'],
        [0x0A, 'o6', 'DVGW'],
        [0x0A, 'o7', 'unused', True],
        [0x07, 'h0', 'Speicher 1'],
        [0x07, 'h1', 'Speicher 1'],
        [0x07, 'h2', 'Speicher 2'],
        [0x07, 'h3', 'Speicher 2'],
        [0x07, 'h4', 'Speicher 3'],
        [0x07, 'h5', 'Speicher 3'],
        [0x0F, 'r0', 'Speicher 1'],
        [0x0F, 'r1', 'Speicher 2'],
        [0x0F, 'r2', 'Speicher 3'],
        [0x0B, 'f0', 'Funktion aktiv'],
        [0x0B, 'f1', 'Solarkreis'],
    ],
    'Ratiofresh200_1261_de' : [
        [0x08, 'd', 'Datum'],
        [0x09, 'm', 'Uhrzeit'],
        [0x10, 's', 'Sekunden'],
        [0x01, 't0', 'T1 Kollektor'],
        [0x01, 't1', 'T2 Speicher oben'],
        [0x01, 't2', 'T3 Speicher unten'],
        [0x01, 't3', 'T4 Rücklaufanh.'],
        [0x01, 't4', 'T5 Rücklaufanh.'],
        [0x01, 't5', 'T6 T', True],
        [0x01, 't6', 'T7 T', True],
        [0x01, 't7', 'T8 Primär Vorlauf'],
        [0x01, 't8', 'T9 Kaltwasser'],
        [0x01, 't9', 'T10 T'],
        [0x01, 't10', 'T11 Frischwasser'],
        [0x0A, 'o0', 'Ausgang 1'],
        [0x0A, 'o1', 'Ausgang 2'],
        [0x0A, 'o2', 'Ausgang 3'],
        [0x0A, 'o3', 'Ausgang 4'],
        [0x0A, 'o4', 'Ausgang 5'],
        [0x0A, 'o5', 'Ausgang 6'],
        [0x0A, 'o6', 'Ausgang 7'],
        [0x0A, 'o7', 'unused', True],
        [0x0D, 'e0', 'Fehler'],
        [0x0D, 'e1', 'Fehler'],
        [0x0E, 'e1', 'Fehler'],
        [0x07, 'h1', 'Ertrag Speicher'],
        [0x00, 'i0', 'Dummy 1', True],
        [0x0F, 'r0', 'Laufzeit Speicher'],
        [0x00, 'i1', 'Dummy 2', True],
    ]
}