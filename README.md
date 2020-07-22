# 다나와 크롤러

각종 PC부품들의 가격의 변동을 알아보기 위해서 제작했습니다

크롤링은 GitHub의 Actions를 사용하여 매일 UTP 0시(한국시간으로 9:00 AM)에 실행되도록 설정하였습니다

Actions의 큐 대기시간과 크롤링에 걸리는 시간(약 10분)이 존재해 보통 9시 3~40분에 완료됩니다


## [크롤링 데이터](https://github.com/sammy310/Danawa_Crawler/tree/master/crawl_data)
- [CPU](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/CPU.csv)
- [그래픽카드](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/VGA.csv)

- [마더보드](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/MBoard.csv)
- [램](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/RAM.csv)

- [SSD](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/SSD.csv)
- [HDD](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/HDD.csv)

- [쿨러](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/Cooler.csv)
- [케이스](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/Case.csv)
- [파워](https://github.com/sammy310/Danawa_Crawler/blob/master/crawl_data/Power.csv)


---

### 제작에 사용된 것들

- Python : 3.7
- Scrapy : 2.1.0
- selenium : 3.141.0
- Chromedriver : 2.40 (linux 64)
