IDLE = 0x7A89C197
SYNC = 0x7CD215D8
preARM = 0xAAAAAAAA
def calc_CRC(data):  # BCH(31,21)校验位计算
    data = data << 10
    mod = 0x76900000
    cmp_value = 0x40000000
    while cmp_value >= 0b10000000000:
        if data & cmp_value != 0:
            data = data ^ mod
        mod = mod >> 1
        cmp_value = cmp_value >> 1
    return data


def evenCheck(data):  # 偶校验算法
    count = 0
    for i in range(32):
        if (data << i) & 0x80000000 > 0:
            count += 1
    if count % 2 == 0:
        return 0
    else:
        return 1


def genAddrCode(addr, function):  # 生成地址码
    addrCode = 0  # 首位置0,地址码标志
    addr = addr >> 3  # 只使用地址的高18位,低三位舍弃
    addrCode = addrCode | (addr << 13)  # 18位地址
    addrCode = addrCode | (function << 11)  # 2位功能位
    addrCode = addrCode | (calc_CRC(addrCode >> 11) << 1)  # 10位CRC校验位
    addrCode = addrCode | evenCheck(addrCode)  # 偶校验位
    return addrCode


def genMsgCode(msgBin):  # 生成信息码，每个码20位
    msgCode = 0x80000000  # 首位置1,信息码标志
    msgCode = msgCode | (msgBin << 11)  # 20位信息
    msgCode = msgCode | (calc_CRC(msgCode >> 11) << 1)  # 10位CRC校验
    msgCode = msgCode | evenCheck(msgCode)  # 偶校验位
    return msgCode

def deCodeString(charBytes):
    encodingType = 'gb2312'
    codeList = []
    charBytes7bit = []
    for char in charBytes:
        if char >= 0b10000000 and encodingType != 'gb2312':
            charBytes7bit.append(0x70)
            encodingType = 'gb2312'
        if char < 0b10000000 and encodingType != 'ascii':
            charBytes7bit.append(0xF0)
            encodingType = 'ascii'
        #char = char & 0b01111111
        char_inverted = 0x00
        for i in range(8):
            char_inverted |= char >> i & 0x01
            if i != 7:
                char_inverted = char_inverted << 1
        charBytes7bit.append(char_inverted&0xFE)


    # 一个信息码可容纳20位数据
    msgBin = 0x00000000
    bitCounter = 0
    for char in charBytes7bit:
        msgBin = msgBin << 1
        for i in range(1,8):  # 遍历每个7位的每一位，并填入msgBin中
            msgBin |= char >> (8 - i) & 0x01
            bitCounter += 1
            if bitCounter == 20:  # 满20位时存入列表，继续下一个码字。
                codeList.append(msgBin)
                bitCounter = 0
                msgBin = 0x00000000
            else:
                msgBin = msgBin << 1
        msgBin = msgBin >> 1
    if msgBin != 0:
        codeList.append(msgBin << (20 - bitCounter))  # 码字空余位置使用0补齐
    msgCode = []
    for code in codeList:
        msgCode.append(genMsgCode(code))
    return msgCode


def genSignal(addr, msg):  # 生成最终的基带信号
    codeList = []
    function = 0
    if msg != "":
        function = 1
        for c in list(msg):
            if c > 128:
                function = 3
    # 生成576位前置码,preARM为32位,重复18次即576位
    for i in range(22):
        codeList.append(preARM)
#     print(codeList)
    # 发送同步码，标志着第一码组开始
    codeList.append(SYNC)
    # 根据地址低三位决定地址码发送帧号，否则发送空闲码
    frameNumber = addr & 0b00000111
    for i in range(8):
        # 如果帧号对应，则在生成地址码后退出循环，否则发送空闲码
        if i == frameNumber:
            code = genAddrCode(addr, function)
            codeList.append(code)
            break
        else:
            codeList.append(IDLE)
            codeList.append(IDLE)

    # 后面紧跟着发送信息码
    # 根据帧号计算出本码组剩余码字数，填补剩余，如果不够，就添加一个同步码再开一个码组
    msgCode = deCodeString(msg)
    codeWordCounter = 0
    endFlag = (8 - frameNumber) * 2 - 1
    for i in range(len(msgCode)):
        codeList.append(msgCode[i])
        codeWordCounter += 1
        if codeWordCounter == endFlag:
            endFlag = 16
            codeList.append(SYNC)
            codeWordCounter = 0

    # 如果信息码总个数为偶数个，那么最后一帧会缺一个码字，用空闲码补全
    if len(msgCode) % 2 == 0:
        codeList.append(IDLE)

    # 如果码组没有用完，用空闲码补全
    if codeWordCounter > 0:
        for i in range(16 - codeWordCounter):
            codeList.append(IDLE)
    else:
        codeList.append(IDLE)

    return codeList