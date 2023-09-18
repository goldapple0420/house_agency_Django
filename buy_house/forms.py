from django import forms

class GetItemsListForm(forms.Form):
    AGENCY_CHOICES = (
        ('1', '台灣房屋'),
        ('2', '永慶房屋'),
        ('3', '信義房屋'),
        ('4', '中信房屋'),
        ('5', '幸福家'),
        ('6', '東龍'),
        ('7', '群義房屋'),
        ('8', '飛鷹'),
        ('9', '僑福房屋'),
        ('10', '惠雙房屋'),
        ('11', 'ERA'),
        ('12', '南北'),
        ('13', '台慶'),
        ('14', '21世紀'),
        ('15', '大家房屋'),
        ('16', '住商'),
        ('17', '全國'),
        ('18', '樂屋網'),
        ('19', '好房網'),
        ('20', '591'),
        ('21', '東森房屋'),
        ('22', '太平洋房屋'),
        ('23', '有巢氏房屋'),
        ('24', '春耕房屋'),
        ('25', '我家網'),
        ('26', '淘屋網'),
        ('27', '愛屋線上'),
        ('28', '777'),
        ('29', '大豐富'),
        ('30', '房屋資訊網'),
        ('31', '房屋媽媽'),
        ('32', '588'),
        ('33', 'yes319')
    )
    CITY_CHOICES = (
        ('A', '臺北市'),
        ('B', '臺中市'),
        ('C', '基隆市'),
        ('D', '臺南市'),
        ('E', '高雄市'),
        ('F', '新北市'),
        ('G', '宜蘭縣'),
        ('H', '桃園市'),
        ('I', '嘉義市'),
        ('J', '新竹縣'),
        ('K', '苗栗縣'),
        ('M', '南投縣'),
        ('N', '彰化縣'),
        ('O', '新竹市'),
        ('P', '雲林縣'),
        ('Q', '嘉義縣'),
        ('T', '屏東縣'),
        ('U', '花蓮縣'),
        ('V', '臺東縣'),
        ('X', '澎湖縣'),
        ('W', '金門縣'),
        ('Z', '連江縣')
    )
    city = forms.MultipleChoiceField(label='縣市', choices=CITY_CHOICES, widget=forms.CheckboxSelectMultiple)
    agency_source = forms.MultipleChoiceField(label='房仲網站', choices=AGENCY_CHOICES, widget=forms.CheckboxSelectMultiple)
    delay_seconds = forms.IntegerField(label='延遲秒數', initial=3)

