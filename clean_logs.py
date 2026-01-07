def clean(inp, out):
    with open(inp) as f, open(out, "w") as o:
        for line in f:
            if "🌾 Crop:" in line:
                o.write(line.split(":")[1].strip() + "\n")

clean("soil_dry.txt", "soil_dry_clean.txt")
clean("soil_normal.txt", "soil_normal_clean.txt")
clean("soil_wet.txt", "soil_wet_clean.txt")
