BTN_CONTINUE = "button:text('Continue')"
BTN_REJECT = "button:text('Reject')"

BTN_SEARCH = '//button[@data-testid="search-button"]'
INPUT_SEARCH = '//input[@data-testid="search-input"]'
BTN_SUBMIT = '//button[@data-test-id="search-submit"]'

BTN_DATE_DROPDOWN = '//div[@aria-label="Date Range"]/button[@data-testid="search-date-dropdown-a"]'
BTN_SPECIFIC_DATES = '//div[@aria-label="Date Range"]/div/ul/li/button[@value="Specific Dates"]'
CAL_FIRST_DAY = '//div[@role="gridcell" and text()="1"]'
BTN_NEXT_MONTH = '//button[@aria-label="Next Month"]'
BTN_PREV_MONTH ='//button[@aria-label="Previous Month"]'
INPUT_START_DATE = '//input[@id="startDate"]'
INPUT_END_DATE ='//input[@id="endDate"]'

BTN_SECTION_DROPDOWN = '//div[@data-testid="section"]/button/label[text()="Section"]'
BTN_SECTION = '//div[@data-testid="section"]/div/ul/li/label/span[text()="{}"]'

BTN_SORT_DROPDOWN = '//select[@data-testid="SearchForm-sortBy"]'

BTN_DATE_DISPLAY = '//button[@facet-name="date"]'

RESULT_LIST = '//li[@data-testid="search-bodega-result"]/div'
BTN_SHOW_MORE = '//button[@data-testid="search-show-more-button"]'

A_TAG = '//a'
DATE_RE = '(?P<date>\d{4}\/\d{2}\/\d{2})'

IMG_TAG = '//div/figure/div/img'
IMG_FILENAME_RE = '.*\/(?P<radix_name>.*).*/(?P<file_name>(?P=radix_name).*\.\w{3,4})'
FILENAME_GROUP_NAME = 'file_name'

TITLE_TAG = '//a/h4'

DESCRIPTION_TAG = '//a/p[@class="css-16nhkrn"]'

MONEY_RE = '(\$\d+((,\d{3})+)?(\.\d{1,2})?)|(\d+ (dollars|USD))'