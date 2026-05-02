def get_size(data):
    bmi = data.weight / ((data.height / 100) ** 2)

    if bmi < 18.5:
        return "S"
    elif bmi < 24.9:
        return "M"
    elif bmi < 29.9:
        return "L"
    else:
        return "XL"