import re

from utils.answers import get_answer, is_correct_answer, get_skill_answer

# print(re.search("years(.*?)((Trading System(.*?)experience(.*?)(have|\\?))|(experience(.*?)(using|with)(.*?)Trading System))", "do you have experience with golang, mongodb, aws, and terraform?", re.IGNORECASE))
answer = get_answer("linkedin", "what nationality?")
print(answer)
# print(is_correct_answer("  South Asian", answer))
# print(get_skill_answer("how many years of work experience do you have with adobe experience manager (aem)?"))