import gdal
import os

RS_path = r''
H = 1000


def read_img(filename):
    dataset = gdal.Open(filename)  # 打开文件

    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数

    im_geotransform = dataset.GetGeoTransform()  # 仿射矩阵
    im_project = dataset.GetProjection()  # 地图投影信息
    im_dataset = dataset.ReadAsArray(0, 0, im_width, im_height)  # 将数据写成数组，对应栅格矩阵

    del dataset
    return im_project, im_geotransform, im_dataset


def write_img(filename, im_geotrans, im_data):
    # gdal数据类型包括
    # gdal.GDT_Byte,
    # gdal .GDT_UInt16, gdal.GDT_Int16, gdal.GDT_UInt32, gdal.GDT_Int32,
    # gdal.GDT_Float32, gdal.GDT_Float64

    # 判断栅格数据的数据类型
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    # 判读数组维数
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape

        # 创建文件
    driver = gdal.GetDriverByName("GTiff")  # 数据类型必须有，因为要计算需要多大内存空间
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset



from osgeo import ogr
import matplotlib.pyplot as plt
from ospybook.vectorplotter import VectorPlotter

#  由线构建多边形
ring = ogr.Geometry(ogr.wkbLinearRing)  #  构建几何类型:线
ring.AddPoint(58, 38.5)  #  添加点01
ring.AddPoint(53, 6)  #  添加点02
ring.AddPoint(99.5, 19)  #  添加点03
ring.AddPoint(73, 42)  #  添加点04
yard = ogr.Geometry(ogr.wkbPolygon)  #  构建几何类型:多边形面
yard.AddGeometry(ring)
yard.CloseRings()

'''画图'''
vp = VectorPlotter(True)  # 调用VectorPlotter类
vp.plot(yard, fill=False, edgecolor='blue')
ring = yard.GetGeometryRef(0)  # 再次创建线，循环构建
for i in range(ring.GetPointCount()):
    ring.SetPoint(i, ring.GetX(i)-5, ring.GetY(i))
vp.plot(yard, fill=False, ec='red', linestyle='dashed')
plt.show()
plt.pause(5)  # 画图窗口显示5秒后自动关闭





import ogr, sys, os

os.chdir(r'E:\')

# 设置driver
driver = ogr.GetDriverByName('ESRI Shapefile')
# 打开输入的矢量
inDs = driver.Open('sites.shp', 0)
if inDs is None:
    print("Could not open", 'sites.shp')
sys.exit(1)
# 打开输入矢量的图册
inLayer = inDs.GetLayer()

# 检查所需创建的矢量是否已存在
if os.path.exists('test.shp'):
    driver.DeleteDataSource('test.shp')
# 创建矢量
outDs = driver.CreateDataSource('test.shp')
if outDs is None:
    print("Could not create file")
sys.exit(1)
# 创建图册
outLayer = outDs.CreateLayer('test', geom_type=ogr.wkbPoint)

# 将输入矢量的属性应用到新矢量
fieldDefn = inLayer.GetFeature(0).GetFieldDefnRef('id')
outLayer.CreateField(fieldDefn)
featureDefn = outLayer.GetLayerDefn()

cnt = 0
inFeature = inLayer.GetNextFeature()
while inFeature:
    outFeature = ogr.Feature(featureDefn)
    outFeature.SetGeometry(inFeature.GetGeometryRef())
    outLayer.CreateFeature(outFeature)
    inFeature.Destroy()
    outFeature.Destroy()

    cnt = cnt + 1
    if cnt < 10:
        inFeature = inLayer.GetNextFeature()
    else:
        break

inDs.Destroy()
outDs.Destroy()
