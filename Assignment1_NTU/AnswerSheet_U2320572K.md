Full Name: Khansa Putri Nugraha

School Email: KHANSAPU001@e.ntu.edu.sg

Matriculation Number: U2320572K

I hereby declare that I will use the knowledge and skills gained from this assignment solely for educational, research, and authorised security purposes. I will not use them to gain unauthorised access, conduct malicious activities, or otherwise cause harm to any individual, organisation, or system.

---

Q1.
```yara
rule is_upx_packed {
    strings: 
        $s1 = "UPX0"
        $s2 = "UPX1"
        $s3 = "UPX2"
        $magic = "UPX!"

    condition:
        uint16(0) == 0x5A4D and ($magic or 2 of ($s*))
}
```

Q2.
```yara
rule is_pe {
    condition:
        // 1. Check for 'MZ' magic bytes at the very beginning (Offset 0)
        // YARA reads the 2-byte address in little-endian, so remember to reverse the byte order!
        uint16(0) == 0x5A4D

        and

        // 2. Check for 'PE\0\0' magic bytes at the address specified in the e_lfanew field
        // The e_lfanew field is always located at offset 0x3C (60) in the DOS header.
        // We read the 4-byte address at 0x3C (e_lfanew field), jump to that address, and check for 0x00004550 (PE\0\0)
        uint32(uint32(0x3C)) == 0x00004550
}
```

Q3.
```yara
import "pe"
rule is_dharma_ransomware {
    meta:
        description = "Detects Dharma Ransomware"

    strings:
        $pdb = "C:\\crysis\\Release\\PDB\\payload.pdb"

    condition:
        $pdb or
        pe.imphash() == "f86dec4a80961955a89e7ed62046cc0e" or
        (
            pe.number_of_imports == 1 and
            pe.imports("KERNEL32.dll", "GetProcAddress") and
            pe.imports("KERNEL32.dll", "LoadLibraryA") and
            pe.imports("KERNEL32.dll", "WaitForSingleObject") and
            pe.imports("KERNEL32.dll", "InitializeCriticalSectionAndSpinCount") and
            pe.imports("KERNEL32.dll", "LeaveCriticalSection") and
            pe.imports("KERNEL32.dll", "GetLastError") and
            pe.imports("KERNEL32.dll", "EnterCriticalSection") and
            pe.imports("KERNEL32.dll", "ReleaseMutex") and
            pe.imports("KERNEL32.dll", "CloseHandle")
        )
}
```

Q4.
```yara
import "pe"
rule is_raccoon_stealer {
    meta:
        description = "Detects RaccoonStealer Infostealer"

    strings:
        // unpacked build string that are hard to change
        $u1  = "discord_files\\"
        $u2  = "wallets\\"
        $u3  = "steamstr"
        $u4  = "inetcomm server passwords"
        $u5  = "outlook account manager passwords"
        $u6  = "abe2869f-9b47-4cd9-a358-c22904dba7f7"
        $u7  = "\\Moonchild Productions\\Pale Moon\\"
        $u8  = "\\WaterFox\\"
        // unpacked build values that are changeable every build
        $u9  = "tS1oI8aQ4.zip"
        $u10 = "lA4-gV5-iK7"
        $u11 = "zD7wC8jM0"
        $u12 = "A:\\_Work\\rc-build-v1-exe\\json.hpp"
        $u13 = "26f3793be8b185aea4eee88e206ef155"

        // packed build
        $p1 = "ozqofauhs8w40psxeo1z6b48uo695n1wweov9c6fhd4k7gz4nsksvoifwwom"
        $p2 = "GASfdrtwyefdeytwr"
        $p3 = "GFASrtefdwtrdwe"
        $p4 = "bZGtARYPF\\AeWG5"
        $p5 = "s8bgnbk6t7ee2ppd06aft20ifrgw1b3gkvz7fy4z4g0jmztp9sxloiuc8go22fms50itacfzjw9a8y8tu3mm3nyv7g"
        $p6 = "9myfb95yy63nihqbpvf5a9krrn44scown4u94dck3x6jfg8vxxj29jzm5j7235ydezrh7h8ng89e7l92657mwp28is"
        $p7 = ".zqHWbqh"

    condition:
        4 of ($u*) or
        3 of ($p*) or
        pe.imphash() == "2f1bba23d3f31d886fd20c963bc55038" or
        pe.imphash() == "d86b72152e3eb79509e879927a109d7c" or
        (
            pe.imports("WINHTTP.dll", "WinHttpOpen") and
            pe.imports("CRYPT32.dll", "CryptUnprotectData") and
            pe.imports("ktmw32.dll", "CreateTransaction") and
            pe.imports("gdiplus.dll", "GdiplusStartup")
        )
}
```

Q5.
```yara
rule is_neuron_service {
    meta:
        description = "Detects NeuronService by Turla Group"

    strings:
        // core logic of malware
        $x1 = "LaskOK"
        $x2 = "KeepAliveLastOK"
        $x3 = "EncryptScript"
        $x4 = "KillOldThread"
        $x5 = "StorageScript"
        $x6 = "CommandScript"

        // helper classes / functions it uses for config and the web server.
        // not unique enough alone, but a bunch of them together is suspicious
        $m1 = "WebServerUtils"
        $m2 = "FindSPath"
        $m3 = "GetSubKey"
        $m4 = "SetValueName"
        $m5 = "AddConfigAsString"
        $m6 = "DelConfigAsString"

        // pretends to be an Exchange service
        // malware's internal name
        $e1 = "neuron_service"
        // fake exe name. the real exe is Microsoft.Exchange.ServiceHost.exe
        $e2 = "Microsoft.Exchange.Service.exe"
        // fake service name. the real service is MSExchangeServiceHost
        $e3 = "MSExchangeService"

    condition:
        2 of ($x*) or
        (1 of ($x*) and 3 of ($m*)) or
        (any of ($e*) and 2 of ($x*)) or
        6 of ($m*)
}
```

Q6.
```yara
rule is_unknown_malware {
    meta:
        description = "Detects SC4016 Unknown Malware"

    strings:
        // core loader logic
        // function names that decrypts and runs the shellcode
        $c1 = "main.encrypted_sc"
        $c2 = "main.decrypt"
        $c3 = "main.key"
        $c4 = "main.checkErr"
        // embedded byte blobs
        $g1 = "main..gobytes.1"
        $g2 = "main..gobytes.2"
        // grab memory, then make it executable so it can run the decrypted
        // file only contains the encrypted version of the payload, only exists decrypted in memory so antivirus does not see it
        $v1 = "golang.org/x/sys/windows.VirtualAlloc"
        $v2 = "golang.org/x/sys/windows.VirtualProtect"

        // author leftovers (build paths, repo name)
        $i1 = "github.com/aidanfora/go-memecats/stub"
        $i2 = "C:/Users/aidan/Storage/yara-executable/go-memecats-v2/stub/stub.go"
        $i3 = "go-memecats"

    condition:
        (2 of ($c*) and 1 of ($g*)) or
        (all of ($v*) and 2 of ($c*)) or
        (1 of ($i*) and 1 of ($c*)) or
        2 of ($i*)
}
```

Q7.
```yara
rule is_wannacry_artifacts {
    meta:
        description = "Identify WannaCry Memory Artifacts"

    strings:
        $kill  = "iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com"
        $mutex = "MsWinZonesCacheCounterMutexA"
        $ext   = ".wnry"
        $d1    = "tasksche.exe"
        $d2    = "mssecsvc.exe"
        $d3    = "taskdl.exe"
        $d4    = "taskse.exe"

    condition:
        all of them
}
```

Q8.
```text
@WanaDecryptor@.exe
```

Q9.
```text
3200, 1716, tasksche.exe
```

Q10.
```text
ueqzlhmlwuxdg271
```

Q11.
```text
\Device\HarddiskVolume1\Intel\ueqzlhmlwuxdg271\00000000.eky
```

Q12.
```text
cmd.exe /c start /b @WanaDecryptor@.exe vs
```

Q13.
```text
taskkill.exe /f /im Microsoft.Exchange.*
taskkill.exe /f /im MSExchange*
taskkill.exe /f /im mysqld.exe
taskkill.exe /f /im sqlserver.exe
taskkill.exe /f /im sqlwriter.exe
```

Q14.
```text
57g7spgrzlojinas.onion
76jdd2ir2embyv47.onion
cwwnhwhlz52maqm7.onion
gx7ekbenv2riucmf.onion
xxlvbrloxvriy2c5.onion
```

Q15.
```text
115p7UMMngoj1pMvkpHijcRdfJNXj6LrLn
13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94
```
