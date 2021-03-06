# Name: cocktaildb.py
# Author: pbzweihander
# Email: sd852456@naver.com
#
# Copyright (C) 2017 pbzweihander
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

import requests
import json


def find_cocktails(name: str, search=False, detailed=False) -> str:
    dlist = get_drinklist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?s=" + name)
    if len(dlist) == 0:
        return ""
    if not dlist:
        return ""
    if (name.lower() in [d.get('strDrink').lower() for d in dlist] or len(dlist) == 1) and not search:
        for d in dlist:
            if d.get('strDrink').lower() == name.lower():
                return parse_cocktail(d, detailed)
    else:
        nlist = [d.get('strDrink') for d in dlist]
        if len(nlist) < 8:
            return ', '.join(nlist)
        else:
            return ', '.join(nlist[:8])


def random_cocktails() -> str:
    dlist = get_drinklist(r"http://www.thecocktaildb.com/api/json/v1/1/random.php")
    d = dlist[0]
    return parse_cocktail(d)


def parse_cocktail(d: dict, detailed=False) -> str:
    name = d.get('strDrink').strip()
    if not name:
        return ""
    glass = (d.get('strGlass') or "").strip()
    ingredients = []
    measures = []
    for i in range(1, 16):
        ii = (d.get("strIngredient%s" % i) or "").strip()
        mm = (d.get("strMeasure%s" % i) or "").strip()
        if len(ii) > 0:
            ingredients.append(ii)
            measures.append(mm)
    s = name + '\n'
    if glass:
        s += glass + '\n'
    for i, m in zip(ingredients, measures):
        if measures:
            s += i + ' - ' + m + '\n'
        else:
            s += i + '\n'
    if detailed:
        s += (d.get("strInstructions") or "").strip()
    return s


def get_drinklist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        dl = json.loads(r.text).get('drinks')
        if dl:
            return list(dl)
    return []


def find_ingredient(name: str, search=False, detailed=False) -> str:
    dlist = get_ingredientlist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?i=" + name)
    if len(dlist) == 0:
        return ""
    if not dlist:
        return ""
    if (name.lower() in [d.get('strIngredient').lower() for d in dlist] or len(dlist) == 1) and not search:
        for d in dlist:
            if name.lower() == d.get('strIngredient').lower():
                return parse_ingredient(d, detailed)
    else:
        nlist = [d.get('strIngredient') for d in dlist]
        if len(nlist) < 8:
            return ', '.join(nlist)
        else:
            return ', '.join(nlist[:8])


def parse_ingredient(d: dict, detailed=False) -> str:
    name = d.get('strIngredient').strip()
    if not name:
        return ""
    stype = (d.get('strType') or "").strip()
    s = name + '\n'
    if stype:
        s += 'Type : ' + stype  # + '\n'
    if detailed:
        s += (d.get("strDescription") or "").strip()
    return s


def get_ingredientlist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        il = json.loads(r.text).get('ingredients')
        if il:
            return list(il)
    return []
