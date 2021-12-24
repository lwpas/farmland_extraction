import os
import sys

try:
    from osgeo import ogr
except ImportError:
    import ogr

import gdal

import cv2
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

raster = r'E:\workspace\tmp\0000001009.tif'  # 上一步导出的tif作为用于裁剪的栅格图像
shp = r'E:\workspace\tmp\Converted_Graphics.shp'  # 用于裁剪的shp
output_file = r'E:\workspace\tmp\sample'  # 裁剪后的保存路径
# output_shp = r'E:\workspace\tmp\1.shp'

size = 128
first_number = 1

if not os.path.exists(output_file):
    os.mkdir(output_file)
    print('样本文件夹已创建')
else:
    print('样本文件夹已存在')


def clip_raster(in_raster, out_raster, mask_shp):
    gdal.Warp(out_raster,
              in_raster,
              format='GTiff',
              dstSRS='EPSG:4326',
              cutlineDSName=mask_shp,
              cropToCutline=True,  # 按掩膜图层范围裁剪
              dstNodata=-9999,
              outputType=gdal.GDT_Float64)


ogr.UseExceptions()
dataSource = ogr.Open(shp)
layer = dataSource.GetLayer()

if dataSource is None:  # 判断是否成功打开
    print('could not open')
    sys.exit(1)
else:
    print('done!')

driver = ogr.GetDriverByName('ESRI Shapefile')  # 载入驱动
# dataSource = driver.Open(shp, 0)  # 第二个参数为0是只读，为1是可写


layer_spatialref = layer.GetSpatialRef()

output_shpfile = output_file + '/' + str(first_number).zfill(10)
if not os.path.exists(output_shpfile):
    os.mkdir(output_shpfile)

output_shp = output_shpfile + '/' + str(first_number).zfill(10) + '.shp'
if os.path.exists(output_shp):  # 应先判断这个要被创建的文件（filename）不能存在，否则会出错
    driver.DeleteDataSource(output_shp)

outdatasource = driver.CreateDataSource(output_shp)

outLayer = outdatasource.CreateLayer(output_shp, layer_spatialref, geom_type=ogr.wkbPolygon)
def_feature = outLayer.GetLayerDefn()

###-----------创建缓冲区范围为0的缓冲区------####
for feature in layer:
    buff_geom = feature.GetGeometryRef().Buffer(128)
    out_feat = ogr.Feature(def_feature)
    out_feat.SetGeometry(buff_geom)
    outLayer.CreateFeature(out_feat)
    out_feat = None
outdatasource.FlushCache()
del dataSource, outdatasource
# out_lyr = None

# feat = layer.GetFeature(0)  # 提取数据层中的第一个要素
# fid = feat.GetField('feature')  # 读取该要素字段名为'FieldID'的值，注意读取'shape'字段会报错
# print(fid)
# geom = feat.GetGeometryRef()  # 提取该要素的轮廓坐标
# print(geom)
# n = layer.GetFeatureCount()  # 该图层中有多少个要素

for feat in layer:
    # point = layer.GetFeature(i)
    # fid = point.GetField('feature')
    point_locate = feat.GetGeometryRef()
    X = point_locate.GetX()
    Y = point_locate.GetY()

dataSource.Destroy()


# 另外还有按顺序读取feature，循环遍历所有的feature
# feat = layer.GetNextFeature() #读取下一个
#
# while feat:
#
#     feat = layer.GetNextFeature()
#
# later.ResetReading() #复位


# 影像库数组转化为gdal_array图片
def img2array(img):
    ima = gdal_array.numpy.fromstring(img.tobytes(), 'b')
    ima.shape = img.im.size[1], img.im.size[0]
    return ima


# 计算地理坐标的像素位置
def world2pixel(geo_mat, x, y):
    ul_x, x_dist, rtn_x, ul_y, rtn_y, y_dist = [geo_mat[i] for i in range(6)]
    pixel = int((x - ul_x) / x_dist)
    line = int((ul_y - y) / abs(y_dist))
    return pixel, line


src_arr = gdal_array.LoadFile(raster)  # 载入数据
# 获取世界文件
src_img = gdal.Open(raster)
geo_trans = src_img.GetGeoTransform()
# 使用pyshp
m_shp = shapefile.Reader("{}.shp".format(shp))  # 打开shp
# 将图层扩展转换为像素坐标
min_x, min_y, max_x, max_y = m_shp.bbox
ul_x, ul_y = world2pixel(geo_trans, min_x, max_y)
lr_x, lr_y = world2pixel(geo_trans, max_x, min_y)
# 计算新图片像素尺寸
px_wid = int(lr_x - ul_x)
px_hei = int(lr_y - ul_y)
clip_img = src_arr[:, ul_y:lr_y, ul_x:lr_x]
# 为图片创建一个新的geomatrix对象以便附加地理参考数据
geo_trans = list(geo_trans)
geo_trans[0] = min_x
geo_trans[3] = max_y
# 边界线
pixels = []
for p in m_shp.shape(0).points:
    pixels.append(world2pixel(geo_trans, p[0], p[1]))
raster_poly = Image.new('L', (px_wid, px_hei), 1)
# 使用PIL创建一个空白图片
raster_rize = ImageDraw.Draw(raster_poly)
raster_rize.polygon(pixels, 0)
# 将PIL转换为numpy
mask_arr = img2array(raster_poly)
# 裁剪
clip_img = gdal_array.numpy.choose(mask_arr, (clip_img, 0)).astype(gdal_array.numpy.uint16)
# 保存为tiff
out = gdal_array.SaveArray(clip_img, output, format='GTiff', prototype=raster)
out = None

# 加载图像康康
NUMS = 65536
cliped = gdal_array.LoadFile(output)
clip_arr = cv2.merge((cliped[0] / float(NUMS), cliped[1] / float(NUMS), cliped[2] / float(NUMS)))
plt.figure(figsize=(10, 10))
plt.imshow(clip_arr)
plt.show()

# extent = layer.GetExtent()
# print('extent:', extent)
# print('ul:', extent[0], extent[1])  # 左右边界
# print('lr:', extent[2], extent[3])  # 下上边界


# def create_polygon(poly_name, poly_location, poly_spatialref):
#     ## 生成面矢量文件 ##
#
#     data_source = driver.CreateDataSource(str(poly_name) + ".shp")  ## shp文件名称
#     # srs = osr.SpatialReference()
#     # srs.ImportFromEPSG(4326) ## 空间参考：WGS84
#     layer_polygon = data_source.CreateLayer(str(poly_name) + ".shp", poly_spatialref, ogr.wkbPolygon)  ## 图层名称要与shp名称一致
#     field_name = ogr.FieldDefn("Name", ogr.OFTString)  ## 设置属性
#     field_name.SetWidth(20)  ## 设置长度
#     layer_polygon.CreateField(field_name)  ## 创建字段
#     field_length = ogr.FieldDefn("Area", ogr.OFTReal)  ## 设置属性
#     layer_polygon.CreateField(field_length)  ## 创建字段
#     field_ID = ogr.FieldDefn("ClassID", ogr.OFTInteger)
#     field_ID.SetWidth(20)
#     layer_polygon.CreateField(field_ID)
#     feature = ogr.Feature(layer_polygon.GetLayerDefn())
#     feature.SetField("Name", "polygon")  ## 设置字段值
#     feature.SetField("Area", "500")  ## 设置字段值
#     feature.SetField("ClassID", "0")
#     wkt = "POLYGON(" + str(poly_location) + ")"  ## 创建面
#     polygon = ogr.CreateGeometryFromWkt(wkt)  ## 生成面
#     feature.SetGeometry(polygon)  ## 设置面
#     layer_polygon.CreateFeature(feature)  ## 添加面
#     feature = None  ## 关闭属性
#     data_source = None
#     return layer_polygon
