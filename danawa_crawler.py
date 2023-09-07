# -*- coding: utf-8 -*-

# danawa_cralwer.py
# sammy310


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#날짜 및 시간 관련 작업, CSV 파일 작업, 파일 및 디렉토리 조작, 예외 처리 등을 위한 모듈을 가져옵니다.
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import csv
import os
import os.path
import shutil
import traceback

#병렬 처리를 위한 multiprocessing.Pool 모듈을 가져옵니다.
from multiprocessing import Pool

#GitHub API를 사용하기 위한 PyGithub 라이브러리에서 Github 클래스를 가져옵니다.
from github import Github

#병렬 처리를 위한 프로세스 수를 설정합니다. 이 예제에서는 2개의 프로세스를 사용합니다.
PROCESS_COUNT = 2

#GitHub에서 사용할 액세스 토큰과 레포지토리 이름을 설정합니다.
GITHUB_TOKEN_KEY = 'MY_GITHUB_TOKEN'
GITHUB_REPOSITORY_NAME = 'hawnble/1'

#크롤링할 카테고리 정보를 담고 있는 CSV 파일의 이름을 설정합니다.
CRAWLING_DATA_CSV_FILE = 'CrawlingCategory.csv'

#크롤링한 데이터를 저장할 디렉토리 경로 및 갱신된 데이터를 저장할 디렉토리 경로를 설정합니다.
DATA_PATH = 'crawl_data'
DATA_REFRESH_PATH = f'{DATA_PATH}/Last_Data'

#시간대를 설정합니다. 이 예제에서는 아시아/서울 시간대를 사용합니다.
TIMEZONE = 'Asia/Seoul'

#크롬 웹 브라우저를 제어하기 위한 크롬 드라이버 파일의 경로를 설정합니다.
# CHROMEDRIVER_PATH = 'chromedriver_94.exe'
CHROMEDRIVER_PATH = 'chromedriver'

#데이터를 구분하고 나누기 위한 구분자를 설정합니다.
DATA_DIVIDER = '---'
DATA_REMARK = '//'
DATA_ROW_DIVIDER = '_'
DATA_PRODUCT_DIVIDER = '|'

#카테고리 정보의 필드 이름을 상수로 설정합니다.
STR_NAME = 'name'
STR_URL = 'url'
STR_CRAWLING_PAGE_SIZE = 'crawlingPageSize'

#DanawaCrawler 클래스를 정의합니다. 이 클래스는 크롤링 및 데이터 처리를 담당합니다.
class DanawaCrawler:
    def __init__(self):
        #오류 목록을 저장하는 빈 리스트를 초기화합니다.
        self.errorList = list()
        #크롤링할 카테고리 정보를 저장하는 빈 리스트를 초기화합니다.
        self.crawlingCategory = list()
        #CRAWLING_DATA_CSV_FILE에 지정된 CSV 파일을 읽기 모드로 엽니다.
        with open(CRAWLING_DATA_CSV_FILE, 'r', newline='') as file:
            #CSV 파일을 한 줄씩 읽어오며, 앞뒤 공백을 제거합니다.
            for crawlingValues in csv.reader(file, skipinitialspace=True):
                #CSV 파일의 각 줄이 주석으로 시작하지 않는 경우에만 아래 코드를 실행합니다.
                if not crawlingValues[0].startswith(DATA_REMARK):
                    #CSV 파일에서 읽어온 값을 파싱하여 카테고리 정보를 딕셔너리로 만들고, self.crawlingCategory 리스트에 추가합니다. 이 딕셔너리는 카테고리의 이름, URL 및 크롤링 페이지 크기를 포함합니다
                    self.crawlingCategory.append({STR_NAME: crawlingValues[0], STR_URL: crawlingValues[1], STR_CRAWLING_PAGE_SIZE: int(crawlingValues[2])})

    def StartCrawling(self):
        #Selenium의 Chrome 웹 드라이버 옵션을 설정하기 위한 webdriver.ChromeOptions() 객체를 생성합니다.
        self.chrome_option = webdriver.ChromeOptions()
        #웹 브라우저를 헤드리스 모드(화면 표시 없이 백그라운드에서 실행)로 실행하기 위한 옵션을 추가합니다.
        self.chrome_option.add_argument('--headless')
        #웹 브라우저 창의 크기를 설정하고 최대화하여 화면에 표시되도록 합니다. GPU 가속을 비활성화합니다.
        self.chrome_option.add_argument('--window-size=1920,1080')
        self.chrome_option.add_argument('--start-maximized')
        self.chrome_option.add_argument('--disable-gpu')
        #웹 브라우저의 언어를 한국어로 설정합니다.
        self.chrome_option.add_argument('lang=ko=KR')

        if __name__ == '__main__':
            #multiprocessing.Pool을 사용하여 병렬로 크롤링 작업을 실행합니다. 
            #PROCESS_COUNT로 설정한 프로세스 수만큼 병렬 작업이 동시에 실행됩니다. 
            #self.CrawlingCategory 메서드가 각 카테고리를 크롤링합니다.
            pool = Pool(processes=PROCESS_COUNT)
            pool.map(self.CrawlingCategory, self.crawlingCategory)
            pool.close()
            pool.join()

            
    #각 카테고리를 크롤링하는 메서드입니다. categoryValue로 크롤링할 카테고리의 정보를 받습니다.
    def CrawlingCategory(self, categoryValue):
        #카테고리 정보에서 이름, URL, 크롤링 페이지 크기를 추출합니다.
        crawlingName = categoryValue[STR_NAME]
        crawlingURL = categoryValue[STR_URL]
        crawlingSize = categoryValue[STR_CRAWLING_PAGE_SIZE]

        #현재 크롤링 중인 카테고리의 이름을 출력합니다.
        print('Crawling Start : ' + crawlingName)

        # data
        #크롤링한 데이터를 저장할 CSV 파일을 생성하고, 헤더 행을 작성합니다.
        crawlingFile = open(f'{crawlingName}.csv', 'w', newline='', encoding='utf8')
        crawlingData_csvWriter = csv.writer(crawlingFile)
        crawlingData_csvWriter.writerow([self.GetCurrentDate().strftime('%Y-%m-%d %H:%M:%S')])

        #크롤링 작업 중에 발생할 수 있는 예외를 처리하기 위한 try-except 블록을 시작합니다.
        try:
            #Chrome 웹 드라이버를 사용하여 웹 브라우저를 엽니다.
            browser = webdriver.Chrome(CHROMEDRIVER_PATH, options=self.chrome_option)
            #웹 페이지 요소를 찾을 때까지 최대 5초 동안 대기합니다.
            browser.implicitly_wait(5)
            #크롤링할 웹 페이지로 이동합니다.
            browser.get(crawlingURL)

            #웹 페이지에서 옵션 요소를 찾아 클릭합니다.
            browser.find_element_by_xpath('//option[@value="90"]').click()
        
            #웹 페이지에서 특정 요소가 사라질 때까지 최대 10초 동안 대기합니다.
            wait = WebDriverWait(browser, 10)
            wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'product_list_cover')))

            #크롤링 페이지 크기만큼 반복합니다. range(-1, crawlingSize)는 -1부터 crawlingSize - 1까지 반복합니다.
            for i in range(-1, crawlingSize):
                #페이지 인덱스가 -1일 때(첫 페이지) 새로운 상품 순으로 정렬합니다.
                if i == -1:
                    browser.find_element_by_xpath('//li[@data-sort-method="NEW"]').click()
                #페이지 인덱스가 0일 때(두 번째 페이지) 인기 상품 순으로 정렬합니다.
                elif i == 0:
                    browser.find_element_by_xpath('//li[@data-sort-method="BEST"]').click()
                #페이지 인덱스가 0보다 크면 다음 페이지로 이동합니다. 
                #페이지 인덱스가 10의 배수일 때는 다음 페이지로 이동하고, 그렇지 않으면 해당 페이지로 이동합니다.
                elif i > 0:
                    if i % 10 == 0:
                        browser.find_element_by_xpath('//a[@class="edge_nav nav_next"]').click()
                    else:
                        browser.find_element_by_xpath('//a[@class="num "][%d]'%(i%10)).click()
                #상품 목록이 로딩될 때까지 최대 10초 동안 대기합니다.
                wait.until(EC.invisibility_of_element((By.CLASS_NAME, 'product_list_cover')))
                
                # Get Product List
                #상품 목록을 찾아서 각 상품 요소를 가져옵니다.
                productListDiv = browser.find_element_by_xpath('//div[@class="main_prodlist main_prodlist_list"]')
                products = productListDiv.find_elements_by_xpath('//ul[@class="product_list"]/li')

                for product in products:
                    ##상품 요소 중 ID 속성이 없는 경우 무시합니다.
                    if not product.get_attribute('id'):
                        continue

                    # ad
                    #광고 상품인 경우 무시합니다.
                    if 'prod_ad_item' in product.get_attribute('class').split(' '):
                        continue
                    #ID가 'ad'로 시작하는 상품인 경우 무시합니다.
                    if product.get_attribute('id').strip().startswith('ad'):
                        continue

                    #상품의 ID, 이름, 제원, 가격 정보를 추출합니다.
                    productId = product.get_attribute('id')[11:]
                    productName = product.find_element_by_xpath('./div/div[2]/p/a').text.strip()
                    
                    '''
                    수정하고 있는 부분 (spec_list 추가)
                    '''
                    productSpec_list = product.find_element_by_xpath('./div/div[2]/dl/dd/div').text.strip()

                    productPrices = product.find_elements_by_xpath('./div/div[3]/ul/li')
                    productPriceStr = ''

                    # Check Mall
                    #상품이 몰 상품인지 여부를 판단합니다.
                    isMall = False
                    if 'prod_top5' in product.find_element_by_xpath('./div/div[3]').get_attribute('class').split(' '):
                        isMall = True
                    
                    #몰 상품의 경우 상품 가격 정보를 추출합니다.
                    if isMall:
                        for productPrice in productPrices:
                            if 'top5_button' in productPrice.get_attribute('class').split(' '):
                                continue

                            #상품 가격 정보를 구분하기 위해 구분자를 추가합니다.
                            if productPriceStr:
                                productPriceStr += DATA_PRODUCT_DIVIDER

                            #몰 이름을 추출합니다.
                            mallName = productPrice.find_element_by_xpath('./a/div[1]').text.strip()
                            if not mallName:
                                mallName = productPrice.find_element_by_xpath('./a/div[1]/span[1]').text.strip()

                            #상품의 가격을 추출합니다.
                            price = productPrice.find_element_by_xpath('./a/div[2]/em').text.strip()

                            #몰 이름과 가격을 결합하여 가격 문자열을 만듭니다.
                            productPriceStr += f'{mallName}{DATA_ROW_DIVIDER}{price}'
                    
                    #몰 상품이 아닌 경우 상품 가격 정보를 추출합니다.
                    else:
                        for productPrice in productPrices:
                            if productPriceStr:
                                productPriceStr += DATA_PRODUCT_DIVIDER
                            
                            # Default
                            #상품 유형과 가격을 추출합니다. 이때 상품 유형은 줄바꿈 문자를 구분자로 사용하고, 순위 정보를 제거합니다.
                            productType = productPrice.find_element_by_xpath('./div/p').text.strip()

                            # like Ram/HDD/SSD
                            # HDD : 'WD60EZAZ, 6TB\n25원/1GB_149,000'
                            productType = productType.replace('\n', DATA_ROW_DIVIDER)

                            # Remove rank text
                            # 1위, 2위 ...
                            productType = self.RemoveRankText(productType)
                            
                            price = productPrice.find_element_by_xpath('./p[2]/a/strong').text.strip()

                            #상품 유형이 있으면 유형과 가격을 결합하고, 없으면 가격만 추가합니다.
                            if productType:
                                productPriceStr += f'{productType}{DATA_ROW_DIVIDER}{price}'
                            else:
                                productPriceStr += f'{price}'

                    #크롤링한 상품 정보를 CSV 파일에 기록합니다.
                    crawlingData_csvWriter.writerow([productId, productName, productSpec_list, productPriceStr])

        #예외 처리 블록을 시작합니다.
        #예외가 발생한 경우 오류 메시지를 출력하고 self.errorList에 오류를 추가합니다.
        except Exception as e:
            print('Error - ' + crawlingName + ' ->')
            print(traceback.format_exc())
            self.errorList.append(crawlingName)

        #크롤링한 데이터를 저장한 CSV 파일을 닫습니다.
        crawlingFile.close()

        #현재 카테고리의 크롤링이 완료되었음을 출력합니다.
        print('Crawling Finish : ' + crawlingName)

    #상품 유형 문자열에서 순위 정보를 제거하는 메서드입니다.
    def RemoveRankText(self, productText):
        #문자열 길이가 2 미만인 경우 그대로 반환합니다.
        if len(productText) < 2:
            return productText

        #첫 번째 문자와 두 번째 문자를 추출합니다.
        char1 = productText[0]
        char2 = productText[1]

        #첫 번째 문자가 숫자이고 1에서 9 사이의 값인 경우, 두 번째 문자가 '위'인 경우에만 순위 정보를 제거하고 문자열을 반환합니다.
        if char1.isdigit() and (1 <= int(char1) and int(char1) <= 9):
            if char2 == '위':
                return productText[2:].strip()
        
        return productText

    #데이터를 정렬하는 메서드입니다.
    def DataSort(self):
        print('Data Sort\n')

        #크롤링한 카테고리 목록을 반복합니다.
        for crawlingValue in self.crawlingCategory:
            #카테고리 이름과 해당 카테고리의 크롤링 데이터 파일 경로를 설정합니다.
            dataName = crawlingValue[STR_NAME]
            crawlingDataPath = f'{dataName}.csv'

            #크롤링 데이터 파일이 존재하지 않는 경우 다음 카테고리로 넘어갑니다.
            if not os.path.exists(crawlingDataPath):
                continue

            #크롤링한 데이터와 기존 데이터를 저장할 리스트를 초기화합니다.
            crawl_dataList = list()
            dataList = list()
            
            #크롤링 데이터 파일을 열고 데이터를 읽어 crawl_dataList에 추가합니다.
            with open(crawlingDataPath, 'r', newline='', encoding='utf8') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    crawl_dataList.append(row)
            
            #크롤링 데이터가 없는 경우 다음 카테고리로 넘어갑니다.
            if len(crawl_dataList) == 0:
                continue
            
            #정렬된 데이터를 저장할 경로를 설정하고 해당 경로에 파일이 없으면 빈 파일을 생성합니다.
            dataPath = f'{DATA_PATH}/{dataName}.csv'
            if not os.path.exists(dataPath):
                file = open(dataPath, 'w', encoding='utf8')
                file.close()
            #정렬된 데이터 파일을 열고 데이터를 읽어 dataList에 추가합니다.
            with open(dataPath, 'r', newline='', encoding='utf8') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    dataList.append(row)
            
            #데이터 리스트가 비어 있는 경우 헤더 행을 추가합니다.
            if len(dataList) == 0:
                dataList.append(['Id', 'Name'])
            
            #크롤링 데이터의 헤더 값을 데이터 리스트의 헤더 행에 추가하고 데이터 크기를 설정합니다.    
            dataList[0].append(crawl_dataList[0][0])
            dataSize = len(dataList[0])

            for product in crawl_dataList:
                ##크롤링 데이터에서 숫자가 아닌 경우를 필터링합니다.
                if not str(product[0]).isdigit():
                    continue
                
                #크롤링 데이터의 상품 ID가 기존 데이터에 이미 존재하는 경우, 가격 정보를 추가하고 isDataExist를 True로 설정합니다.
                isDataExist = False
                for data in dataList:
                    if data[0] == product[0]:
                        if len(data) < dataSize:
                            data.append(product[2])
                            data.append(product[3])
                        isDataExist = True
                        break

                #isDataExist가 False인 경우 새로운 데이터 리스트를 생성하고 가격 정보를 추가합니다.
                if not isDataExist:
                    newDataList = ([product[0], product[1]])
                    for i in range(2,len(dataList[0])-1):
                        newDataList.append(0)
                    newDataList.append(product[2])
                    newDataList.append(product[3])
                
                    #새로운 데이터 리스트를 기존 데이터 리스트에 추가합니다.
                    dataList.append(newDataList)
                
            #모든 데이터가 동일한 크기를 가지도록 데이터를 패딩합니다.
            for data in dataList:
                if len(data) < dataSize:
                    for i in range(len(data),dataSize):
                        data.append(0)
                
            #상품 데이터 헤더 행을 추출하고 데이터 리스트에서 제거합니다.
            productData = dataList.pop(0)
            #데이터 리스트를 상품 이름을 기준으로 정렬합니다.
            dataList.sort(key= lambda x: x[1])
            #정렬된 상품 데이터 헤더 행을 다시 리스트 맨 앞에 추가합니다.
            dataList.insert(0, productData)

            #정렬된 데이터를 파일에 씁니다.
            with open(dataPath, 'w', newline='', encoding='utf8') as file:
                csvWriter = csv.writer(file)
                for data in dataList:
                    csvWriter.writerow(data)
                file.close()

            #크롤링 데이터 파일을 삭제합니다.
            if os.path.isfile(crawlingDataPath):
                os.remove(crawlingDataPath)

    #데이터를 갱신하는 메서드입니다.
    def DataRefresh(self):
        dTime = self.GetCurrentDate()
        #현재 날짜를 가져와서 날짜가 1일인 경우에만 아래 코드를 실행합니다.
        if dTime.day == 1:
            print('Data Refresh\n')

            #데이터 디렉토리가 존재하지 않으면 생성합니다.
            if not os.path.exists(DATA_PATH):
                os.mkdir(DATA_PATH)

            #현재 날짜에서 하루를 뺀 날짜를 계산하고, 해당 날짜를 'YYYY-MM' 형식의 문자열로 변환합니다.
            dTime -= timedelta(days=1)
            dateStr = dTime.strftime('%Y-%m')

            #갱신된 데이터를 저장할 디렉토리 경로를 설정하고 해당 디렉토리가 없으면 생성합니다.
            dataSavePath = f'{DATA_REFRESH_PATH}/{dateStr}'
            if not os.path.exists(dataSavePath):
                os.mkdir(dataSavePath)
            
            #데이터 디렉토리에서 CSV 파일을 찾아서 갱신된 데이터 디렉토리로 이동합니다.
            for file in os.listdir(DATA_PATH):
                fileName, fileExt = os.path.splitext(file)
                if fileExt == '.csv':
                    filePath = f'{DATA_PATH}/{file}'
                    refreshFilePath = f'{dataSavePath}/{file}'
                    shutil.move(filePath, refreshFilePath)
    
    #현재 날짜와 시간을 가져오는 메서드입니다.
    def GetCurrentDate(self):
        #지정된 시간대로 현재 날짜와 시간을 반환합니다.
        tz = timezone(TIMEZONE)
        return (datetime.now(tz))

    #오류를 GitHub 이슈로 생성하는 메서드입니다.
    def CreateIssue(self):
        #오류 리스트에 오류가 있는 경우에만 아래 코드를 실행합니다.
        if len(self.errorList) > 0:
            #GitHub 토큰을 사용하여 GitHub 리포지토리를 연결합니다.
            g = Github(os.environ[GITHUB_TOKEN_KEY])
            repo = g.get_repo(GITHUB_REPOSITORY_NAME)

            #이슈 제목과 본문을 설정합니다. 본문에는 오류 리스트의 내용을 포함합니다.
            title = f'Crawling Error - ' + self.GetCurrentDate().strftime('%Y-%m-%d')
            body = ''
            for err in self.errorList:
                body += f'- {err}\n'
            #오류 라벨을 추가하여 이슈를 생성합니다.
            labels = [repo.get_label('bug')]
            repo.create_issue(title=title, body=body, labels=labels)
        


if __name__ == '__main__':
    crawler = DanawaCrawler()
    crawler.DataRefresh()
    crawler.StartCrawling()
    crawler.DataSort()
    crawler.CreateIssue()
