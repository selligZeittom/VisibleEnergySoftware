# -*- coding: utf-8 -*-

import json
import logging
import os
import ssl
import sys
import time

import paho.mqtt.client as mqtt
from cloudio.mqtt_helpers import MqttConnectOptions, MqttReconnectClient
from utils import datetime_helpers
from utils import path_helpers

logging.getLogger(__name__).setLevel(logging.INFO)


class MqttClient:

    MQTT_ERR_SUCCESS = mqtt.MQTT_ERR_SUCCESS

    log = logging.getLogger(__name__)

    def __init__(self, configFile):
        """
        Initializer of a MQTT Client Thread
        Initialize all attributes of the MQTT Client
        configure the username and the password, the TLS certificate and connect to the broker
        :param configFile: Allow to configure MQTT attributes easier (file inside the project)
        """
        self._isConnected = False
        self._useReconnectClient = False             # Chooses the MQTT client
        config = self.parseConfigFile(configFile)

        '''client variables'''
        self._qos = int(config['cloudio']['qos'])
        self._endPointName = config['endpoint']['name']
        self._nodeName = config['node']['name']
        self._certificate = config['cloudio']['certificate']
        self._userName = config['cloudio']['username']
        self._password = config['cloudio']['password']
        self._host = config['cloudio']['host']
        self._port = int(config['cloudio']['port'])
        self._subscribe = config['cloudio']['subscribe_topics']
        self._exportPower = 0
        self._importPower = 0
        self._ambientTemp = 0
        self._exportEnergy = 0
        self._importEnergy = 0
        self._importTariff = 0
        self._exportTariff = 0
        self._PM1 = 0
        self._PM2 = 0
        self._PM3 = 0
        self._maxValue = 8000
        self.log.info('Starting MQTT client...')

        if not self._useReconnectClient:
            self._client = mqtt.Client()
            self._client.on_connect = self.onConnect
            self._client.on_disconnect = self.onDisconnect
            self._client.on_message = self.onMessage

            self._client.username_pw_set(self._userName, self._password)
            self._client.tls_set(ca_certs=self._certificate, tls_version=ssl.PROTOCOL_TLSv1_2)
            self._client.tls_insecure_set(True)
            self._clientId = self._client.connect(self._host, port=self._port, keepalive=60)
            self._client.loop_start()
        else:
            self.connectOptions = MqttConnectOptions()
            self.connectOptions._username = config['cloudio']['username']
            self.connectOptions._password = config['cloudio']['password']
            self.connectOptions._clientCertFile = config['cloudio']['certificate']
            self._client = MqttReconnectClient(config['cloudio']['host'],
                                               clientId=self._endPointName + '-client-',
                                               clean_session=False,
                                               options=self.connectOptions)

            # Register callback method for connection established
            self._client.setOnConnectedCallback(self.onConnected)
            # Register callback method to be called when receiving a message over MQTT
            self._client.setOnMessageCallback(self.onMessage)

            self._client.start()

    def connect(self, host, port=1883, keepalive=60, bind_address=""):
        """Connect to a remote broker.

        host is the hostname or IP address of the remote broker.
        port is the network port of the server host to connect to. Defaults to
        1883. Note that the default port for MQTT over SSL/TLS is 8883 so if you
        are using tls_set() the port may need providing.
        keepalive: Maximum period in seconds between communications with the
        broker. If no other messages are being exchanged, this controls the
        rate at which the client will send ping messages to the broker.
        """
        self.connect_async(host, port, keepalive, bind_address)
        return self.reconnect()

    def close(self):
        """
        Disconnect to a remote broker
        """
        if not self._useReconnectClient:
            self._client.disconnect()
        else:
            self._client.stop()

    def parseConfigFile(self, configFile):
        global config

        from configobj import ConfigObj

        config = None

        pathConfigFile = path_helpers.prettify(configFile)

        if pathConfigFile and os.path.isfile(pathConfigFile):
            config = ConfigObj(pathConfigFile)

        if config:
            # Check if most important configuration parameters are present
            assert 'cloudio' in config, 'Missing group \'cloudio\' in config file!'
            assert 'endpoint' in config, 'Missing group \'endpoint\' in config file!'
            assert 'node' in config, 'Missing group \'node\' in config file!'
            assert 'host' in config['cloudio'], 'Missing \'host\' parameter in cloudio group!'
            assert 'port' in config['cloudio'], 'Missing \'port\' parameter in cloudio group!'
            assert 'username' in config['cloudio'], 'Missing \'username\' parameter in cloudio group!'
            assert 'password' in config['cloudio'], 'Missing \'password\' parameter in cloudio group!'
            assert 'subscribe_topics' in config['cloudio'], 'Missing \'subscribe_topics\' parameter in cloudio group!'
            assert 'qos' in config['cloudio'], 'Missing \'qos\' parameter in cloudio group!'
            assert 'name' in config['endpoint'], 'Missing \'name\' parameter in endpoint group!'
            assert 'name' in config['node'], 'Missing \'name\' parameter in node group!'
        else:
            sys.exit(u'Error reading config file')

        return config

    def waitTilConnected(self):
        """
        Allow to keep alive the thread
        """
        while True:
            time.sleep(0.2)

    def onConnect(self, client, userdata, flags, rc):
        """
        Callback method called when a message arrive from the broker

        :param client: Don't used
        :param userdata: Don't used
        :param flags: Don't used
        :param rc: flag to know if the connection is done:
                        0: Connection successful
                        1: Connection refused - incorrect protocol version
                        2: Connection refused - invalid client identifier
                        3: Connection refused - server unavailable
                        4: Connection refused - bad username or password
                        5: Connection refused - not authorised
        """
        if rc == 0:
            self._isConnected = True
            print("hello I'm connected")
            (result, mid) = self._client.subscribe(u'@update/goflex-dc-053.nodes/#', 1)
            if result == self.MQTT_ERR_SUCCESS:
                print('subscribe done')
            else:
                print('subscribe fail')

    def onConnected(self):
        self._isConnected = True

    def onDisconnect(self, client, userdata, rc):
        """
        Called when the client disconnects from the broker
        :param client: Don't used
        :param userdata: Don't used
        :param rc: flag to know the state of disconnection
                        0: expected disconnection
                        else: unexpected disconnection
        """
        self.log.info('Disconnect: ' + str(rc))
        print("goodbye I'm disconnected")

    def onMessage(self, client, userdata, msg):
        """
        Called when a message come from the broker.

        The data is contain in the payload of the message in the form of JSON File
        :param client: Don't used
        :param userdata: Don't used
        :param msg: Instance of MQTTMessage which contains the topic, the payload, the qos and the retain
        """
        # active power import
        if msg.topic.find("obis_1_0_1_7_0_255_2") != -1:
            self._importPower = json.loads(msg.payload)['value']
        # active power export
        if msg.topic.find("obis_1_0_2_7_0_255_2") != -1:
            self._exportPower = json.loads(msg.payload)['value']
        # ambient temperature
        if msg.topic.find('ambientSensor-1.objects.temperature') != -1:
            self._ambientTemp = json.loads(msg.payload)['value']
        # import energy
        if msg.topic.find('obis_1_1_1_8_0_255_2') != -1:
            self._importEnergy = json.loads(msg.payload)['value']
        # export energy
        if msg.topic.find('obis_1_1_2_8_0_255_2') != -1:
            self._exportEnergy = json.loads(msg.payload)['value']
        # import tariff
        if msg.topic.find('obis_1_1_1_8_1_255_2') != -1:
            self._importTariff = json.loads(msg.payload)['value']
        # export tariff
        if msg.topic.find('obis_1_1_2_8_1_255_2') != -1:
            self._exportTariff = json.loads(msg.payload)['value']
        # Hot Water for house 49
        if msg.topic.find('powerMeter-1/objects/voltsTotal') != -1:
            self._PM1 = json.loads(msg.payload)['value']
        # Heating for house 49
        if msg.topic.find('powerMeter-2/objects/wattsTotal') != -1:
            self._PM2 = json.loads(msg.payload)['value']
        # Solar panel for house 49
        if msg.topic.find('powerMeter-3/objects/wattsTotal') != -1:
            self._PM3 = json.loads(msg.payload)['value']

    def getExportPower(self):
        """

        :return: the value of the power exported
        """
        return self._exportPower

    def getImportPower(self):
        """

        :return: the value of the power imported
        """
        return self._importPower

    def getAmbientTemp(self):
        """

        :return: the value of ambient temperature
        """
        return self._ambientTemp

    def getExportEnergy(self):
        """

        :return: the value of energy exported
        """
        return self._exportEnergy

    def getImportEnergy(self):
        """

        :return: the value of the energy imported
        """
        return self._importEnergy

    def getImportTariff(self):
        """

        :return: the actual price of imported kWh
        """
        return self._importTariff

    def getExportTariff(self):
        """

        :return: the actual price of exported kWh
        """
        return self._exportTariff

    def getPM1(self):
        """

        :return: the power of the boiler of hot water
        """
        return self._PM1

    def getPM2(self):
        """

        :return: the power of the boiler of heating
        """
        return self._PM2

    def getPM3(self):
        """

        :return: the power of solar panel
        """
        return self._PM3

    def getMaxValue(self):
        return self._maxValue
