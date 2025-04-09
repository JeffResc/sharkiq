from sharkiq import get_ayla_api, OperatingModes, Properties, PowerModes

USERNAME = 'me@email.com'
PASSWORD = '$7r0nkP@s$w0rD'

ayla_api = get_ayla_api(USERNAME, PASSWORD)
ayla_api.sign_in()

shark_vacs = ayla_api.get_devices()
shark = shark_vacs[0]

shark.update()
shark.set_operating_mode(OperatingModes.START)
shark.return_to_base()
