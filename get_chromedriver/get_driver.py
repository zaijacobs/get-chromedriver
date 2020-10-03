import requests
from bs4 import BeautifulSoup
import zipfile
from get_chromedriver import constants
from get_chromedriver.platforms import Platforms
from get_chromedriver import retriever
from get_chromedriver.exceptions.unknown_platform import UnknownPlatform
from get_chromedriver.exceptions.release_url_error import ReleaseUrlError
from get_chromedriver.exceptions.unknown_release import UnknownRelease


class GetChromeDriver:

    def __init__(self, platform):
        self.__available_platforms = Platforms()
        self.__current_set_platform = self.__check_platform(platform)

    def latest_stable_release_version(self):
        """ Return the latest stable release version """

        result = requests.get(constants.CHROMEDRIVER_CHROMIUM_URL)
        soup = BeautifulSoup(result.content, 'html.parser')
        a_tag = soup.select_one(constants.STABLE_RELEASE_CSS_SELECTOR)
        release = a_tag.text.split()[-1]
        self.__check_release(release)
        return release

    def latest_beta_release_version(self):
        """ Return the latest beta release version """

        result = requests.get(constants.CHROMEDRIVER_CHROMIUM_URL)
        soup = BeautifulSoup(result.content, 'html.parser')
        a_tag = soup.select_one(constants.BETA_RELEASE_CSS_SELECTOR)
        release = a_tag.text.split()[-1]
        self.__check_release(release)
        return release

    def latest_stable_release_url(self):
        """ Return the latest stable release url """

        return self.release_url(self.latest_stable_release_version())

    def latest_beta_release_url(self):
        """ Return the latest beta release url """

        return self.release_url(self.latest_beta_release_version())

    def release_url(self, release):
        """ Return the release download url """

        self.__check_release(release)

        url = ''
        if self.__current_set_platform == self.__available_platforms.win:
            url = constants.CHROMEDRIVER_STORAGE_URL + '/' + release + '/' + constants.FILE_NAME_CHROMEDRIVER_WIN_ZIP
        elif self.__current_set_platform == self.__available_platforms.linux:
            url = constants.CHROMEDRIVER_STORAGE_URL + '/' + release + '/' + constants.FILE_NAME_CHROMEDRIVER_LINUX_ZIP
        elif self.__current_set_platform == self.__available_platforms.mac:
            url = constants.CHROMEDRIVER_STORAGE_URL + '/' + release + '/' + constants.FILE_NAME_CHROMEDRIVER_MAC_ZIP

        self.__check_url(url)
        return url

    def download_latest_stable_release(self, output_path=None, extract=False):
        """ Download the latest stable chromedriver release """

        self.download_release(self.latest_stable_release_version(), output_path, extract)

    def download_latest_beta_release(self, output_path=None, extract=False):
        """ Download the latest stable chromedriver release """

        self.download_release(self.latest_beta_release_version(), output_path, extract)

    def download_release(self, release, output_path=None, extract=False):
        """ Download a chromedriver release """

        self.__check_release(release)
        url = self.release_url(release)

        def download(platform_arch):
            if output_path is None:
                output_path_no_file_name = constants.DIR_DOWNLOADS + '/' + release + '/' + platform_arch
            else:
                output_path_no_file_name = output_path

            output_path_with_file_name, file_name = retriever.download(url=url, output_path=output_path_no_file_name)

            if extract:
                with zipfile.ZipFile(output_path_with_file_name, 'r') as zip_ref:
                    zip_ref.extractall(path=output_path_no_file_name)

        if self.__current_set_platform == self.__available_platforms.win:
            download(self.__available_platforms.win_arch)
        elif self.__current_set_platform == self.__available_platforms.linux:
            download(self.__available_platforms.linux_arch)
        elif self.__current_set_platform == self.__available_platforms.mac:
            download(self.__available_platforms.mac_arch)

    def __check_url(self, url):
        """ Check if url is valid """

        if requests.head(url).status_code != 200:
            raise ReleaseUrlError('Invalid url (Possible cause: non-existent release version)')

    def __check_release(self, release):
        """ Check if release format is valid """

        split_release = release.split('.')

        for number in split_release:
            if not number.isnumeric():
                raise UnknownRelease('Invalid release format')

    def __check_platform(self, platform):
        """ Check if platform is valid """

        if platform not in self.__available_platforms.list:
            raise UnknownPlatform('Choose a platform from: ' + str(self.__available_platforms.list))
        return platform
