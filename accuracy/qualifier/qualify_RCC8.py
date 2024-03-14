# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 12:25:10 2018

@author: s_jan001

RCC11: Captures the Topological relations between
    Polygoanl features

"""

#from de9im import pattern
from qualifier.utils_i4l import pattern

DC_pattern = pattern('FF*FF****')
EC_pattern = pattern('FF*F0****' or 'FF*F1****')
PO_pattern = pattern('T*T***T**')
NTPP_pattern = pattern('T*F**F***')
NTPP_inv_pattern = pattern('T*****FF*')
TPP_pattern = pattern('2FF10F212' or '2FF11F212')
TPP_inv_pattern = pattern('212F01FF2' or '212F11FF2')
EQ_pattern = pattern('T*F**FFF*')


def polygonal_topology(p1, p2):
    im_pattern = p1.relate(p2)

    # return im_pettern
    if (DC_pattern.matches(im_pattern)):
        return "dc"
    elif (EC_pattern.matches(im_pattern)):
        return "ec"
    elif (PO_pattern.matches(im_pattern)):
        return "po"
    elif (NTPP_pattern.matches(im_pattern)):
        return "ntpp"
    elif (NTPP_inv_pattern.matches(im_pattern)):
        return "ntppi"
    elif (TPP_pattern.matches(im_pattern)):
        return "tpp"
    elif (TPP_inv_pattern.matches(im_pattern)):
        return "tppi"
    elif (EQ_pattern.matches(im_pattern)):
        return "eq"
    else:
        return None


def qualify_rcc8(data):
    qcn = []
    for i in range(len(data[:-1])):
        for sec in data[i + 1:]:
            if (data[i]['geometry'].geom_type == 'Polygon' and sec['geometry'].geom_type == 'Polygon'):
                o1 = data[i]['attributes']['id']
                o2 = sec['attributes']['id']
                qcn.append(
                    {'obj 1': o1, 'obj 2': o2, 'relation': polygonal_topology(data[i]['geometry'], sec['geometry'])})

    return 'RCC8', 2, {}, qcn