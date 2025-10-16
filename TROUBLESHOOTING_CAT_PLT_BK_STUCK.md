# CAT PLT BK STUCK - Troubleshooting Guide

## IMMEDIATE ACTION
**Press the START button on your jig** - this will reset the error and attempt the operation again.

## ROOT CAUSE ANALYSIS

### What "CAT PLT BK STUCK" Means:
- **CAT** = Cartridge
- **PLT** = Plate 
- **BK** = Back/Backward
- **STUCK** = Mechanical jam or sensor failure

The cartridge positioning plate cannot move to the backward position, or the BW_SNS sensor (RC0) is not detecting it.

## TROUBLESHOOTING STEPS

### 1. **Physical Inspection** ⚠️ (POWER OFF FIRST)
```
□ Turn OFF power to the jig
□ Remove any cartridges from the stack
□ Manually check if the cartridge plate can move freely
□ Look for physical obstructions (debris, bent parts, etc.)
□ Check if the plate mechanism is jammed or binding
□ Ensure the cartridge pusher can slide smoothly
```

### 2. **Sensor Check** (BW_SNS - RC0)
```
□ Verify BW_SNS sensor wiring (RC0 on PIC18F4550)
□ Check sensor mounting - is it properly aligned?
□ Test sensor by manually triggering it (should click/activate)
□ Measure sensor voltage (should be 0V when triggered, 5V when not)
□ Clean sensor lens/surface if optical sensor
```

### 3. **Actuator Check** (PLATE_UD - RA2)
```
□ Verify PLATE_UD actuator wiring (RA2 on PIC18F4550)
□ Check pneumatic/hydraulic lines (if applicable)
□ Test actuator manually - does it extend/retract properly?
□ Check for air leaks or low pressure (pneumatic systems)
□ Verify solenoid operation (should hear click when activated)
```

### 4. **Timing Issues**
```
□ The plate has 10 seconds to move to back position
□ If movement is very slow, may need mechanical adjustment
□ Check for worn bearings, low pressure, or friction
```

## FIRMWARE OPERATION SEQUENCE

When this error occurs, the firmware was executing:
```
1. PLATE_UD = 0      → Move plate UP/BACK
2. CAT_FB = 0        → Set cartridge position to BACK  
3. Wait BW_SNS HIGH  → Wait for backward sensor (RC0)
4. Timeout = 10000ms → If no sensor signal, show error
```

## QUICK TEST PROCEDURE

### Manual Reset Test:
1. **Press START** on jig (attempt automatic recovery)
2. **Watch the plate movement** - does it move at all?
3. **Listen for actuator sounds** - clicking, air pressure, etc.
4. **Check if error repeats** - mechanical vs electrical issue

### Electrical Test:
1. **Power ON** the jig
2. **Check LED indicators** on PIC board (if present)
3. **Verify Pi ↔ PIC communication** working
4. **Test with empty stack** first

## HARDWARE PIN REFERENCE

| Pin | Signal | Description |
|-----|--------|------------|
| RC0 | BW_SNS | Backward sensor (detects plate at back) |
| RA2 | PLATE_UD | Plate up/down actuator (0=up/back) |
| RE0 | CAT_FB | Cartridge forward/back position |

## PREVENTION MEASURES

- **Regular maintenance**: Clean sensors and lubricate moving parts
- **Proper loading**: Don't overload cartridge stack
- **Gentle operation**: Avoid forcing cartridges
- **Environmental**: Keep dust and debris away from mechanisms

## RELATED ERRORS

- `CAT PLT FW STUCK` - Forward movement stuck
- `MCH PLT U STUCK` - Mech plate up movement stuck  
- `PASS PLT STUCK` - Pass plate stuck
- `REJECT PLT STUCK` - Reject plate stuck

All indicate similar mechanical/sensor issues in different parts of the system.

---

**If error persists after mechanical checks, there may be a hardware failure requiring maintenance.**