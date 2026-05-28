import pandas as pd

def load_data(filepath="dataset/camera_dataset.csv"):
    df = pd.read_csv(filepath)
    df = df.dropna()
    df = df[df["Max resolution"] > 0]
    df = df[df["Price"] > 0]
    df = df[df["Weight (inc. batteries)"] > 0]
    kolom = [
        "Model",
        "Release date",
        "Max resolution",
        "Low resolution",
        "Effective pixels",
        "Zoom wide (W)",
        "Zoom tele (T)",
        "Normal focus range",
        "Macro focus range",
        "Storage included",
        "Weight (inc. batteries)",
        "Dimensions",
        "Price",
    ]
    return df[kolom].reset_index(drop=True)


def get_tipe_kriteria():
    return {
        "Release date":             "benefit",
        "Max resolution":           "benefit",
        "Low resolution":           "benefit",
        "Effective pixels":         "benefit",
        "Zoom wide (W)":            "benefit",
        "Zoom tele (T)":            "benefit",
        "Normal focus range":       "cost",
        "Macro focus range":        "cost",
        "Storage included":         "benefit",
        "Weight (inc. batteries)":  "cost",
        "Dimensions":               "cost",
        "Price":                    "cost",
    }


def get_bobot_default():
    return {
        "Release date":             0.05,
        "Max resolution":           0.15,
        "Low resolution":           0.05,
        "Effective pixels":         0.15,
        "Zoom wide (W)":            0.05,
        "Zoom tele (T)":            0.10,
        "Normal focus range":       0.08,
        "Macro focus range":        0.07,
        "Storage included":         0.05,
        "Weight (inc. batteries)":  0.10,
        "Dimensions":               0.05,
        "Price":                    0.10,
    }


if __name__ == "__main__":
    df = load_data()
    print("=== Info Dataset ===")
    print(f"Jumlah data : {len(df)} kamera")
    print(f"Kolom       : {list(df.columns)}")
    print()
    print("=== 5 Data Pertama ===")
    print(df.head().to_string())
    print()
    print("=== Tipe Kriteria ===")
    for k, v in get_tipe_kriteria().items():
        print(f"  {k:<30} → {v}")
    print()
    print("=== Bobot Default ===")
    for k, v in get_bobot_default().items():
        print(f"  {k:<30} → {v}")
    print(f"  Total bobot: {sum(get_bobot_default().values())}")
    df.to_csv("dataset/dataset_clean.csv", index=False)
    print()
    print("dataset_clean.csv berhasil disimpan!")