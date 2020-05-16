import requests
import json

#Returns Product URL for good
def getProdURL(site_url: str, search_item: str):
	request_url = site_url + '/products.json'
	r = requests.get(request_url)
	products = json.loads((r.text))['products']

	for product in products:
		if product['title'] == search_item:
			product_url = site_url + '/products/' + product['handle']
			return product_url
	return False

def getAllGoods(site_url: str):
	request_url = site_url + '/products.json'
	r = requests.get(request_url)
	products = json.loads((r.text))['products']
	prodList = []
	for product in products:
		productName = product['title']
		prodList.append(productName)

	return prodList

#Return dictionary with key being the product name and the value being [prodId, prodTitle, prodPrice, isProdAvaliable, srcLink]
def getProdDict(site_url: str):
	request_url = site_url + '/products.json'
	r = requests.get(request_url)

	products = json.loads((r.text))['products']
	prodDict = {}

	for product in products:
		productName = product['title']
		for i in range(0, len(product['variants'])):
			#get values for dictionary 
			curr_prod_info = product['variants'][i]
			prodId = curr_prod_info['id']
			isProdAvaliable = curr_prod_info['available']
			prodTitle = curr_prod_info['title']
			prodPrice = curr_prod_info['price']
			
			#See if there is an image URL or title 
			srcLink = ('No Image' if not curr_prod_info['featured_image'] else curr_prod_info['featured_image']['src'])
			prodTitle = 'No Title' if prodTitle == 'Default Title' else prodTitle
			if not productName in prodDict:
				prodDict[productName] = [[prodId, prodTitle, prodPrice, isProdAvaliable, srcLink]]
			else:
				prodDict[productName].append([prodId, prodTitle, prodPrice, isProdAvaliable, srcLink])
	return prodDict

# site_url = 'https://foodstirs.com'
# search_item = 'Variety Snack Pack'
# print(getProdURL(site_url, search_item))

site_url = 'https://ugmonk.com/'
# print(getProdDict(site_url))

print(getAllGoods(site_url))