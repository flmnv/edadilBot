from time import time

from src.edadil import Edadil


class Schedule:
    async def update_edadil(self):
        edadil = Edadil()

        start_time = time()

        print('Обновление данных с сайта Едадил...')
        result = await edadil.update()

        if result is True:
            return print(f'Обновление данных с сайта Едадил завершено за {round(time() - start_time, 2)} сек.')

        return print('При обновлении данных с сайте Едадил произошла ошибка')
