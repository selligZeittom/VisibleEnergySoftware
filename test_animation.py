from HardwareManager import ledsMeter

consumption = ledsMeter(addressI2C=0x72, isInConsumption=True, valuePeak=8000)
production = ledsMeter(addressI2C=0x71, isInConsumption=False, valuePeak=8000)

consumption.animation()
production.animation()