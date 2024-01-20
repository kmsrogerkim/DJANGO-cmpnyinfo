class YoungCmpny(Exception):
    '''
    Error that is raised when there are less than 6 years of finstate for the company
    ''' 
    def __init__(self, corp_code: str, end_year: str):
        self.value = end_year
        self.message = f"-----The company({corp_code}) don't have any finstate before {end_year}!------"

    def __str__(self):
        return self.message
		
class StockPriceError(Exception):
    def __init__(self, message, value):
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return self.message