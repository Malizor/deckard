# Deckard, a Web based Glade Runner
# Copyright (C) 2013  Nicolas Delvaux <contact@nicolas-delvaux.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Mapping between locales codes and languages names in the relative locale

It would be better and cleaner to replace this by a library like PyICU
http://pyicu.osafoundation.org or Babel http://pythonhosted.org/Babel.

However, tests revealed that they currently don't support all locales that we
expose and that there is no way to know from APIs if a locale is RTL, which
would be a nice thing to have to adapt the UI (this was fixed in ICU 51).

For now, this list seems to be the only working solution.
"""

locale_language_mapping = {
    'POSIX': 'No translation',
    'af_ZA': 'Afrikaans',
    'am_ET': 'አማርኛ',
    'an_ES': 'Aragonés',
    'ar_AE': 'العربية',
    'as_IN': 'অসমীয়া',
    'ast_ES': 'Asturianu',
    'az_AZ': 'Azərbaycan dili',
    'be_BY': 'беларуская мова',
    'bem_ZM': 'Chibemba',
    'bn_IN': 'বাংলা',
    'brx_IN': 'बड़ो',
    'bs_BA': 'Bosanski',
    'ca_ES': 'Català',
    'cs_CZ': 'Čeština',
    'da_DK': 'Dansk',
    'de_DE': 'Deutsch',
    'el_GR': 'ελληνικά',
    'en_AU': 'English (Australia)',
    'en_US': 'English (US)',
    'eo': 'Esperanto',
    'es_ES': 'Español',
    'et_EE': 'Eesti keel',
    'eu_ES': 'Euskara',
    'fi_FI': 'Suomi',
    'fr_FR': 'Français',
    'fur_IT': 'Furlan',
    'gd_GB': 'Gàidhlig',
    'gl_ES': 'Galego',
    'gu_IN': 'ગુજરાતી',
    'he_IL': 'עִבְרִית',
    'hi_IN': 'हिन्दी',
    'hr_HR': 'Hrvatski jezik',
    'hu_HU': 'Magyar',
    'hy_AM': 'Հայերէն',
    'id_ID': 'Bahasa Indonesia',
    'is_IS': 'Íslenska',
    'it_IT': 'Italiano',
    'ja_JP': '日本語',
    'kn_IN': 'ಕನ್ನಡ',
    'ko_KR': '한국말',
    'lt_LT': 'Lietuvių kalba',
    'lv_LV': 'Latviešu valoda',
    'mai_IN': 'মৈথিলী',
    'mg_MG': 'Malagasy',
    'mk_MK': 'Македонски јазик',
    'ml_IN': 'മലയാളം',
    'mn_MN': 'Монгол хэл',
    'mr_IN': 'मराठी',
    'ms_MY': 'Bahasa Melayu',
    'my_MM': 'မြန်မာစာ',
    'nb_NO': 'Bokmål',
    'nds_NL': 'Plattdüütsch',
    'ne_NP': 'नेपाली',
    'nl_NL': 'Nederlands',
    'nn_NO': 'Nynorsk',
    'nso_ZA': 'Sesotho sa Leboa',
    'oc_FR': 'Occitan',
    'or_IN': 'ଓଡ଼ିଆ',
    'pa_IN': 'ਪੰਜਾਬੀ',
    'pl_PL': 'Język polski',
    'pt_BR': 'Português (Brasil)',
    'pt_PT': 'Português',
    'ro_RO': 'Română',
    'ru_RU': 'Pусский язык',
    'rw_RW': 'Ikinyarwanda',
    'si_LK': 'සිංහල',
    'sk_SK': 'Slovenčina',
    'sl_SI': 'Slovenščina',
    'sq_AL': 'Shqip',
    'sr_RS': 'српски',
    'sv_SE': 'Svenska',
    'ta_IN': 'தமிழ்',
    'te_IN': 'తెలుగు',
    'tg_TJ': 'тоҷикӣ',
    'th_TH': 'ภาษาไทย',
    'tr_TR': 'Türkçe',
    'ug_CN': 'ئۇيغۇرچە',
    'uk_UA': 'Українська',
    'uz_UZ': 'Ўзбек',
    'vi_VN': 'Tiếng Việt',
    'wa_BE': 'Walloon',
    'xh_ZA': 'IsiXhosa',
    'zh_CN': '汉语',
    'zh_HK': '汉语 (香港)',
    'zh_TW': '汉语 (臺灣)',
    'zu_ZA': 'IsiZulu'
}
