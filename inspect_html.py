
with open('zara_dump.html', 'r', encoding='utf-8') as f:
    for line in f:
        if "product-detail-size-selector" in line or "size-list-item" in line:
            # Print chunks of the line since it might be very long
            idx = line.find("product-detail-size-selector")
            if idx != -1:
                print(line[idx:idx+300])
