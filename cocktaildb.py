
import requests
import json


def find_cocktails(name: str) -> str:
    dlist = get_drinklist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?s=" + name)
    if len(dlist) == 0:
        return ""
    if dlist[0].get('strDrink').strip().lower() == name.lower():
        return parse_cocktail(dlist[0])
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


def parse_cocktail(d: dict) -> str:
    name = d.get('strDrink').strip()
    if not name:
        return ""
    glass = (d.get('strGlass') or "").strip()
    ingredients = []
    measures = []
    for i in range(1, 16):
        ii = d.get("strIngredient%s" % i).strip()
        mm = d.get("strMeasure%s" % i).strip()
        if len(ii) > 0 and len(mm) > 0:
            ingredients.append(ii)
            measures.append(mm)
    instruction = (d.get("strInstructions") or "").strip()
    s = name + '\n'
    if glass:
        s += glass + '\n'
    for i, m in zip(ingredients, measures):
        s += i + ' - ' + m + '\n'
    s += instruction
    return s


def get_drinklist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        dl = json.loads(r.text).get('drinks')
        if dl:
            return list(dl)
    return []


def find_ingredient(name: str) -> str:
    dlist = get_ingredientlist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?i=" + name)
    if len(dlist) == 0:
        return ""
    if not dlist:
        return ""
    if dlist[0].get('strIngredient').strip().lower() == name.lower():
        return parse_ingredient(dlist[0])
    else:
        nlist = [d.get('strIngredient') for d in dlist]
        if len(nlist) < 8:
            return ', '.join(nlist)
        else:
            return ', '.join(nlist[:8])


def parse_ingredient(d: dict) -> str:
    name = d.get('strIngredient').strip()
    if not name:
        return ""
    stype = (d.get('strType') or "").strip()
    description = (d.get("strDescription") or "").strip()
    s = name + '\n'
    if stype:
        s += 'Type : ' + stype + '\n'
    s += description
    return s


def get_ingredientlist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        il = json.loads(r.text).get('ingredients')
        if il:
            return list(il)
    return []