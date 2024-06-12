import scrapy
import os
from scrapy.crawler import CrawlerProcess
from dotenv import load_dotenv

load_dotenv()
main_dir = os.getenv("MAIN_DIR")
def extract_text_and_save(urls):
  
  output_dir=main_dir
  class TextExtractorSpider(scrapy.Spider):
      name = "text_extractor"
      start_urls = urls  

      def parse(self, response):
          text_content = response.xpath('//text()').getall()
          plain_text = "\n".join(text_content)
          starting_point = plain_text.find("UNITED STATES")
          print(starting_point) 
          plain_text = plain_text[starting_point:]

          filename = response.url.split('/')[-1] + '.txt'
          output_path = os.path.join(output_dir, filename)
          with open(output_path, 'w', encoding='utf-8') as f:
              f.write(plain_text)

          self.log(f"Text content extracted and saved to: {filename}")


  process = CrawlerProcess()
  process.crawl(TextExtractorSpider)
  process.start()