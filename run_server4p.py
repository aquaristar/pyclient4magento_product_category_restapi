from abcmagento_server import ABCMagentoRESTClient
from pprint import pprint
import csv
import os
import urllib
import xml.etree.cElementTree as etree

def runCategory():
    with open('catemast.csv', 'r') as f:
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
    f = open('catemast.csv', 'r')
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
      <stock_data>
        <qty>1</qty>
        <is_in_stock>1</is_in_stock>
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

        imageXML = """<?xml version="1.0"?><magento_api><image_url>%s</image_url></magento_api>""" % product.find('image').text

abcmagento = ABCMagentoRESTClient()
#abcmagento.retrieveCategories()
#runCategory()
runProduct()