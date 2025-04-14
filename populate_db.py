import os
import django
import random
from datetime import datetime, timedelta
import sys

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otslej.settings')
    print('Инициализация Django...')
    django.setup()
    print('Django успешно инициализирован')

    from transport.models import Transport, Cargo, TransportStatus
    print('Модели успешно импортированы')

    LOCATIONS = [
        'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
        'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону'
    ]

    TRANSPORT_NAMES = [
        'КАМАЗ-5490', 'МАЗ-5440', 'Volvo FH', 'Scania R500', 'Mercedes-Benz Actros',
        'DAF XF', 'MAN TGX', 'Iveco Stralis', 'Renault T-Series', 'КАМАЗ-54901'
    ]

    CARGO_TYPES = [
        'Продукты питания', 'Строительные материалы', 'Мебель', 'Электроника',
        'Одежда', 'Автозапчасти', 'Бытовая техника', 'Медикаменты'
    ]

    TRANSPORT_TYPES = [
        'Грузовик', 'Фургон', 'Рефрижератор', 'Контейнеровоз', 'Автоцистерна'
    ]

    TRANSPORT_STATUSES = ['loading', 'in_transit', 'customs', 'delivered', 'delayed', 'cancelled']

    def create_transport():
        for name in TRANSPORT_NAMES:
            transport = Transport.objects.create(
                number=name,
                type=random.choice(TRANSPORT_TYPES),
                capacity=random.uniform(5.0, 40.0),
                status=random.choice(TRANSPORT_STATUSES),
                current_location=random.choice(LOCATIONS)
            )
            
            for _ in range(5):
                timestamp = datetime.now() - timedelta(days=random.randint(1, 30))
                TransportStatus.objects.create(
                    transport=transport,
                    status=random.choice(TRANSPORT_STATUSES),
                    location=random.choice(LOCATIONS),
                    timestamp=timestamp,
                    comment=f'Статус обновлен {timestamp.strftime("%d.%m.%Y")}'
                )

    def create_cargo():
        transports = Transport.objects.all()
        
        for _ in range(20):
            sender_location = random.choice(LOCATIONS)
            receiver_location = random.choice([loc for loc in LOCATIONS if loc != sender_location])
            cargo_type = random.choice(CARGO_TYPES)
            
            Cargo.objects.create(
                transport=random.choice(transports),
                description=f'Груз {cargo_type} из {sender_location} в {receiver_location}',
                weight=random.uniform(0.1, 50.0),
                volume=random.uniform(0.5, 100.0),
                sender=f'Отправитель из {sender_location}',
                receiver=f'Получатель из {receiver_location}'
            )

    if __name__ == '__main__':
        try:
            print('Начинаем очистку существующих данных...')
            Transport.objects.all().delete()
            Cargo.objects.all().delete()
            TransportStatus.objects.all().delete()
            print('Существующие данные очищены')
            
            print('Создание транспортных средств...')
            create_transport()
            print(f'Создано транспортных средств: {Transport.objects.count()}')
            
            print('Создание грузов...')
            create_cargo()
            print(f'Создано грузов: {Cargo.objects.count()}')
            
            print('Готово! База данных заполнена тестовыми данными.')
        except Exception as e:
            print(f'Произошла ошибка: {str(e)}')
            print(f'Тип ошибки: {type(e).__name__}')
            sys.exit(1)
except Exception as e:
    print(f'Произошла ошибка при инициализации: {str(e)}')
    print(f'Тип ошибки: {type(e).__name__}')
    sys.exit(1) 