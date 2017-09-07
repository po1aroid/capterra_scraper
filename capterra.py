import os
import csv
import requests
from lxml import etree as etree

URL_MAIN = 'http://www.capterra.com'
WORK_DIR = os.path.dirname(os.path.abspath(__file__))


class CapterraScraper:
    def __init__(self):
        self.s = requests.session()

    def create_category(self, category, category_url):
        """
        Write CSV file with all software in category
        :param category: category name
        :param category_url: category URL
        """
        with open(f'{WORK_DIR}/result_{category}.csv', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')

            # Write header of CSV file
            writer.writerow(['App Name', 'Developer', 'Short Description', 'About This Software', 'Product Details',
                             'Vendor Details', 'Pricing'])

            res = self.s.request(method='GET', url=f'{URL_MAIN}/{category_url}')
            product_l = etree.HTML(res.text).xpath("//div[contains(@id,'product-')]")
            for p in product_l:
                # Name
                name = p.xpath("div/div[2]/div/div[1]/h2/a/text()")[0].strip()

                # Developer
                developer = p.xpath("div/div[2]/div/div[1]/h3/text()")[0].replace('by ', '').strip()

                # Short Description
                short_description = p.xpath("div/div[2]/div/div[3]/p[1]/text()")[0].strip()

                product = {'name': name, 'developer': developer, 'short_description': short_description}

                product_url = p.xpath("div/div[2]/div/div[3]/p[1]/a")[0].attrib['href']

                res = self.s.request(method='GET', url=f'{URL_MAIN}{product_url}')
                product_html = etree.HTML(res.text)

                main_div = product_html.xpath("//div[@class='site-main']")[0]

                # About
                product['about'] = main_div.xpath(
                    "div[3]/div/div/div[contains(string(), 'About This Software')]/div[1]/p/text()")[0]

                # Product Details
                pd = main_div.xpath("div[3]/div/div/div[contains(string(), 'Product Details')]/ul[2]")
                p_details = ''
                pricing = ''
                if len(pd) > 0:
                    li_l = pd[0].xpath("li")
                    for li in li_l:
                        if li.xpath("div/div[1]/strong/text()")[0] in ['Starting Price', 'Pricing Details']:
                            pricing += li.xpath("div/div[2]/text()")[0]
                        else:
                            p_details += ''.join(li.xpath("div/div/descendant::text()")).replace('\n', '')
                product['p_details'] = p_details
                product['pricing'] = pricing

                # Vendor Details
                vd = main_div.xpath("div[3]/div/div/div[contains(string(), 'Vendor Details')]/ul[3]")
                if len(vd) > 0:
                    product['v_details'] = vd[0].xpath("string()").strip().replace('\n', '; ')

                # Write row in CSV file
                writer.writerow([product['name'], product['developer'], product['short_description'], product['about'],
                                 product['p_details'], product.get('v_details', None), product['pricing']])

    def main(self):
        """
        Iterate categories
        """
        res = self.s.request(method='GET', url=f'{URL_MAIN}/categories')
        html = etree.HTML(res.text)

        category_link_l = html.xpath("//li[@data-alias-name]/a")
        for link in category_link_l:
            self.create_category(category=link.text, category_url=link.attrib['href'])


if __name__ == '__main__':
    CapterraScraper().main()
    
