@property
def concurrent_keywords(self):
    return ['*','Concurrently ', '(background) Given ', '(background) When ', '(background) Then ', '(background) And ']

def match_stepline(self,token):
    keywords = (self.dialect.given_keywords +
                self.dialect.when_keywords +
                self.dialect.then_keywords +
                self.dialect.and_keywords +
                self.dialect.concurrent_keywords +
                self.dialect.but_keywords)
    for keyword in (k for k in keywords if token.line.startswith(k)):
        title = token.line.get_rest_trimmed(len(keyword))
        self._set_token_matched(token, 'StepLine', title, keyword)
        return True

    return False
