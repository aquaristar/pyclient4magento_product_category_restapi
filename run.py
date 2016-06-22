from abcmagentocli import ABCMagentoRESTClient
from pprint import pprint
import csv
import os
import urllib
import xml.etree.cElementTree as etree
import base64

def runCategory():
	with open('catemast2.csv', 'r') as f:
	    reader = csv.reader(f)
	    for row in reader:
	        categoryId = row[0]
	        categoryName = row[1]
	        parentId = row[2]
	        print categoryId, categoryName, parentId
	        categoryXML = """<?xml version="1.0"?><magento_api><entity_id>%s</entity_id><name>%s</name><is_active>1</is_active><parent_id>%s</parent_id></magento_api>""" % (categoryId, urllib.quote(categoryName), parentId)
	        print categoryXML
	        abcmagento.createCategory(categoryXML)
	    f.close

def getCategoryIdByName(cat_name):
	#print cat_name
	cat_id = 2
	f = open('catemast1.csv', 'r')
	reader = csv.reader(f)
	for row in reader:
		if (row[1] == cat_name):
			cat_id = row[0]
			break
	return cat_id

def runProduct():
	xmlpath = "abcsyncall.xml"
	tree = etree.parse(xmlpath)
	productlist = tree.getroot()
	for product in productlist:
		productXML = """<?xml version="1.0"?>
<magento_api>
      <attribute_set_id>9</attribute_set_id>
      <type_id>simple</type_id>
      <brand>%s</brand>
      <mfn_num>%s</mfn_num>
      <sku>%s</sku>
      <name>%s</name>
      <description>LD</description>
      <short_description>SD</short_description>
      <price>%s</price>
      <special_price>%s</special_price>
      <weight>1.0000</weight>
      <status>%s</status>
      <visibility>4</visibility>
      <tax_class_id>2</tax_class_id>
      <news_from_date>10/12/2015</news_from_date>
      <stock_data>
        <qty>50.0000</qty>
        <min_qty>0.0000</min_qty>
        <use_config_min_qty>1</use_config_min_qty>
        <is_qty_decimal>0</is_qty_decimal>
        <backorders>0</backorders>
        <use_config_backorders>1</use_config_backorders>
        <min_sale_qty>1.0000</min_sale_qty>
        <use_config_min_sale_qty>1</use_config_min_sale_qty>
        <max_sale_qty>0.0000</max_sale_qty>
        <use_config_max_sale_qty>1</use_config_max_sale_qty>
        <is_in_stock>1</is_in_stock>
        <notify_stock_qty></notify_stock_qty>
        <use_config_notify_stock_qty>1</use_config_notify_stock_qty>
        <manage_stock>0</manage_stock>
        <use_config_manage_stock>1</use_config_manage_stock>
        <use_config_qty_increments>1</use_config_qty_increments>
        <qty_increments>0.0000</qty_increments>
        <use_config_enable_qty_inc>1</use_config_enable_qty_inc>
        <enable_qty_increments>0</enable_qty_increments>
        <is_decimal_divided>0</is_decimal_divided>
        <use_config_enable_qty_increments>1</use_config_enable_qty_increments>
      </stock_data>
</magento_api>
""" % (product.find('brand').text, product.find('mfn_Num').text, product.find('sku').text, product.find('name').text, product.find('price').text, product.find('saleprice').text, product.find('availability').text)
		print productXML
		pResponse = abcmagento.createProduct(productXML)

		arrCategory = []
		category = product.find('category')
		if category != None:
			categoryXML = """<?xml version="1.0"?><magento_api><category_id>%s</category_id></magento_api>""" % getCategoryIdByName(category.text)
			arrCategory.append(categoryXML)
			for subCategory in product.findall('Sub_category'):
				categoryXML = """<?xml version="1.0"?><magento_api><category_id>%s</category_id></magento_api>""" % getCategoryIdByName(subCategory.text)
				arrCategory.append(categoryXML)
		print arrCategory
		abcmagento.bindProduct2Category(pResponse,arrCategory)


		image_name = product.find('image').text.split('/')[-1]
		image_path = "D:/JohnHartunian/src/local.abcwarehouse.com/media/product_images/"
		sku = product.find('sku').text
		image_file = image_path + sku + "_large.jpg"
		f = open(image_file, "rb")
		ima = f.read()
		b64ima = ima.encode("base64")
		f.close()

		imageXML="""<?xml version="1.0"?>
		<magento_api>
		<file_mime_type>image/jpeg</file_mime_type>
		<file_content>%s</file_content>
		<file_name>%s</file_name>
		</magento_api>"""%( b64ima, image_name )
		#print b64ima
		r = abcmagento.bindImage2Product(pResponse, imageXML)

		image_label = sku + "_large"
		# image_type =  image_name.split('.')[0].split('_')[1]

		# if image_type == 'large':
		# 	image_type = 'image'
		# elif image_type == 'detail':
		# 	image_type = 'small_image'
		# else:
		# 	image_type = 'thumbnail'

		imageUpdateXML = """<?xml version="1.0"?>
		<magento_api>
		<label>%s</label>
		<exclude>1</exclude>
		<types><data_item>image</data_item></types>
		</magento_api>"""%image_label
		abcmagento.updateImageInfo(r, imageUpdateXML)



		image_file = image_path + sku + "_detail.jpg"
		f = open(image_file, "rb")
		ima = f.read()
		b64ima = ima.encode("base64")
		f.close()

		imageXML="""<?xml version="1.0"?>
		<magento_api>
		<file_mime_type>image/jpeg</file_mime_type>
		<file_content>%s</file_content>
		<file_name>%s</file_name>
		</magento_api>"""%( b64ima, image_name )
		#print b64ima
		r = abcmagento.bindImage2Product(pResponse, imageXML)

		image_label = sku + "_detail"
		imageUpdateXML = """<?xml version="1.0"?>
		<magento_api>
		<label>%s</label>
		<exclude>1</exclude>
		<types><data_item>small_image</data_item></types>
		</magento_api>"""%(image_label)
		abcmagento.updateImageInfo(r, imageUpdateXML)



		image_file = image_path + sku + "_thumb.jpg"
		f = open(image_file, "rb")
		ima = f.read()
		b64ima = ima.encode("base64")
		f.close()

		imageXML="""<?xml version="1.0"?>
		<magento_api>
		<file_mime_type>image/jpeg</file_mime_type>
		<file_content>%s</file_content>
		<file_name>%s</file_name>
		</magento_api>"""%( b64ima, image_name )
		#print b64ima
		r = abcmagento.bindImage2Product(pResponse, imageXML)

		image_label = sku + "_thumb"
		imageUpdateXML = """<?xml version="1.0"?>
		<magento_api>
		<label>%s</label>
		<exclude>1</exclude>
		<types><data_item>thumbnail</data_item></types>
		</magento_api>"""%(image_label)
		abcmagento.updateImageInfo(r, imageUpdateXML)



abcmagento = ABCMagentoRESTClient()
#abcmagento.retrieveCategories()
runProduct()