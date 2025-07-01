import qrcode

def ascii_qr(url: str, invert: bool=False):
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    height = len(matrix)
    width = len(matrix[0])
    rows = []

    for y in range(0, height, 2):
        line = ""
        for x in range(width):
            top = matrix[y][x]
            bottom = matrix[y+1][x] if y + 1 < height else False

            if invert:
                if top and bottom:
                    line += "█"
                elif top and not bottom:
                    line += "▀"
                elif not top and bottom:
                    line += "▄"
                else:
                    line += " "
            else:
                if top and bottom:
                    line += " "
                elif top and not bottom:
                    line += "▄"
                elif not top and bottom:
                    line += "▀"
                else:
                    line += "█"

        rows.append(line)

    return "\n".join(rows)
