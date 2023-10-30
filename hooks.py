class ApiPartMock:
    description: str
    image_url: str
    supplier_link: str
    SKU: str
    manufacturer: str
    manufacturer_link: str
    MPN: str
    quantity_available: float
    packaging: str
    category_path: list[str]
    parameters: dict[str, str]
    price_breaks: dict[int, float]
    currency: str

def fix_amplifier_categories(api_part: ApiPartMock):
    amplifier_type = api_part.parameters.get("Amplifier Type")
    if "OPAMP" in api_part.description:
        api_part.category_path.append("Operational Amplifiers")
    elif "INST" in api_part.description or amplifier_type == "Instrumentation":
        api_part.category_path.append("Instrumentation Amplifiers")
    elif amplifier_type == "General Purpose":
        api_part.category_path.append("Operational Amplifiers")

def fix_resistor_mounting_type(api_part: ApiPartMock):
    if "surface mount" in api_part.category_path[-1].lower():
        api_part.parameters["Mounting Type"] = "Surface Mount"
    if "through hole" in api_part.category_path[-1].lower():
        api_part.parameters["Mounting Type"] = "Through Hole"

def fix_transistor_categories(api_part: ApiPartMock):
    if "BJT" in api_part.category_path[-1] or "Bipolar (BJT)" in api_part.category_path:
        transistor_type = api_part.parameters.get("Transistor Type", "")
        if "NPN" in transistor_type:
            api_part.category_path.append("NPN")
        elif "PNP" in transistor_type:
            api_part.category_path.append("PNP")
    elif "JFETs" in api_part.category_path[-1]  or "JFETs" in api_part.category_path:
        fet_type = api_part.parameters.get("FET Type", "")
        if "N-Channel" in fet_type:
            api_part.category_path.append("N-Channel JFETs")
        elif "P-Channel" in fet_type:
            api_part.category_path.append("P-Channel JFETs")
    elif "FETs" in api_part.category_path[-1] or "FETs, MOSFETs" in api_part.category_path:
        fet_type = api_part.parameters.get("FET Type", "")
        if "N-Channel" in fet_type:
            api_part.category_path.append("N-Channel MOSFETs")
        elif "P-Channel" in fet_type:
            api_part.category_path.append("P-Channel MOSFETs")

def fix_film_capacitor_mounting_type(api_part: ApiPartMock):
    if api_part.category_path[-1] == "Film Capacitors":
        if product := api_part.parameters.get("Product"):
            if "SMD" in product:
                api_part.parameters["Mounting Type"] = "Surface Mount"
            else:
                api_part.parameters["Mounting Type"] = "Through Hole"

def fix_solder_categories(api_part: ApiPartMock):
    if api_part.category_path[-1] == "Solder":
        if solder_type := api_part.parameters.get("Type"):
            api_part.category_path.append(solder_type)

def fix_usb_connector_categories(api_part: ApiPartMock):
    if api_part.category_path[-1] in {"USB, DVI, HDMI Connectors", "USB Connectors"}:
        if connector_type := api_part.parameters.get("Connector Type"):
            for subcategory in ("USB-A", "USB-B", "USB-C"):
                if subcategory in connector_type:
                    api_part.category_path.append(subcategory)
                    break
        elif connector_type := api_part.parameters.get("Type"):
            if "Type C" in connector_type:
                api_part.category_path.append("USB-C")

def fix_lcsc_pin_headers(api_part: ApiPartMock):
    if pin_structure := api_part.parameters.get("Pin Structure"):
        pin_structure = pin_structure.lower()
        if "x" in pin_structure:
            rows, contacts = pin_structure.split("x", 1)
            contacts = contacts.replace("p", "")
            api_part.parameters["Number of Rows"] = rows
            api_part.parameters["Number of Contacts"] = contacts

def fix_motor_type(api_part: ApiPartMock):
    motor_type = []
    for param in ("Motor Type - Stepper", "Motor Type - AC, DC"):
        if param in api_part.parameters:
            motor_type.append(api_part.parameters.pop(param))
    if motor_type:
        motor_type = filter(lambda string: string != "-", motor_type)
        api_part.parameters["Motor Type"] = ", ".join(motor_type)

def fix_duplicate_manufacturers(api_part: ApiPartMock):
    if not api_part.manufacturer:
        return
    if api_part.manufacturer in {"ALPSALPINE",}:
        api_part.manufacturer = "Alps Alpine"
    elif api_part.manufacturer in {"BI Technologies / TT Electronics",}:
        api_part.manufacturer = "TT Electronics/BI"
    elif "Vishay" in api_part.manufacturer:
        api_part.manufacturer = "Vishay"
    elif api_part.manufacturer in {"EPCOS - TDK Electronics",}:
        api_part.manufacturer = "TDK Corporation"

def fix_codecs_categories(api_part: ApiPartMock):
    if not api_part.category_path[-1] == "CODECS":
        return
    if "Audio" in api_part.parameters["Type"]:
        api_part.category_path.append("Audio Codecs")
        if number_of_adcs_dacs := api_part.parameters.get("Number of ADCs / DACs"):
            if "/" in number_of_adcs_dacs:
                n_adcs, n_dacs = number_of_adcs_dacs.split("/", 1)
                api_part.parameters["Number of A/D Converters"] = n_adcs.strip()
                api_part.parameters["Number of D/A Converters"] = n_dacs.strip()

def fix_tme_breadboards(api_part: ApiPartMock):
    if not api_part.category_path[-1] == "Universal PCBs":
        return
    parameters = api_part.parameters
    if "solderless" in parameters.get("Board variant", ""):
        api_part.category_path.append("Breadboards")
    if (width := parameters.get("Width")) and (length := parameters.get("Length")):
        parameters["Size"] = f"{width} ~ {length}"

def fix_tme_idc_connectors(api_part: ApiPartMock):
    if not api_part.category_path[-1] == "IDC connectors":
        return
    if api_part.parameters.get("Connector") == "plug":
        api_part.category_path.append("Connector Housings")
    else:
        api_part.category_path.append("Pin headers")

def fix_tme_headers(api_part: ApiPartMock):
    if not api_part.category_path[-1] == "Pin headers":
        return
    if api_part.parameters.get("Kind of connector") == "male":
        api_part.category_path.append("Headers")
        api_part.parameters["Connector Type"] = "Header"
    elif api_part.parameters.get("Kind of connector") == "female":
        api_part.category_path.append("Sockets")
        api_part.parameters["Connector Type"] = "Socket"

def fix_tme_number_of_rows(api_part: ApiPartMock):
    if "x" in (layout := api_part.parameters.get("Connector pinout layout", "")):
        api_part.parameters["Number of Rows"] = layout.split("x")[0]

SMD_PACKAGES = ["SMD", "SOT-89-3"]
THT_PACKAGES = ["HC-49S", "TO-92", "Plugin", "TO-92-3", "TO-92L"]
PACKAGE_TO_MOUNTING_TYPE = {
    package: mount
    for packages, mount in ((SMD_PACKAGES, "Surface Mount"), (THT_PACKAGES, "Through Hole"))
    for package in packages
}

def fix_mounting_type(api_part: ApiPartMock):
    if "Mounting Type" in api_part.parameters:
        return
    if package_type := api_part.parameters.get("Package Type"):
        for subtype in package_type.split(","):
            if mounting_type := PACKAGE_TO_MOUNTING_TYPE.get(subtype):
                api_part.parameters["Mounting Type"] = mounting_type
                break

MOUNTING_TYPE_MAP = {
    "SMT": "Surface Mount",
    "THT": "Through Hole",
}
def fix_mounting_type_terminology(api_part: ApiPartMock):
    if mounting := api_part.parameters.get("Electrical mounting"):
        api_part.parameters["Mounting Type"] = MOUNTING_TYPE_MAP.get(mounting, mounting)
