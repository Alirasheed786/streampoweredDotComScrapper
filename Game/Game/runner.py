import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'crawl',
            'Game',

        ]
    )
except SystemExit:
    pass

# sudo docker run -it -p 8050:8050 --rm scrapinghub/splash
