import qrcode

# QR kodu veriler(odalar için veriler)
rooms = {
    "LIVINGROOM": "ROOM=LIVINGROOM",
    "KITCHEN": "ROOM=KITCHEN",
    "BEDROOM": "ROOM=BEDROOM",
    "TOILET": "ROOM=TOILET"
}

# QR kodlarını oluştur ve kaydet
for room, data in rooms.items():
    qr = qrcode.QRCode(
        version=1,  
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  
        border=4, 
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(f"/home/ubuntu/catkin_ws/src/odev/maps/qr_codes/{room.lower()}_qr.png")
    print(f"{room} QR kodu oluşturuldu.")

