from PIL import Image, ImageOps

im = ImageOps.mirror(ImageOps.flip(Image.open('pictures/img.png')))
im.show()
icon = Image.new('RGBA', (im.width * 2 - 30, im.height * 2 - 30), (0, 0, 0, 0))

row = Image.new('RGBA', (im.width * 2, im.height), (0, 0, 0, 0))
im_m = ImageOps.mirror(im)
row.paste(im, (0, 0), im.split()[3])
row.paste(im_m, (im.width - 30, 0), im_m.split()[3])
row_f = ImageOps.flip(row)
icon.paste(row, (0, 0), row.split()[3])
icon.paste(row_f, (0, im.height - 30), row_f.split()[3])

#icon.show()
icon.save('pictures/sample2.png')
