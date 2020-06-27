def select_dates(potential_dates):
    list_names = []
    for info in potential_dates:
        if info["age"] > 30 and "art" in info["hobbies"] \
                and info["city"] == "Berlin":
            list_names.append(info["name"])

    return ", ".join(list_names)
