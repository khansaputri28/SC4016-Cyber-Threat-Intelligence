# Assignment 1: ***Y***et ***A***nother ***R***ule-writing ***A***ssignment

<br>

## Part 1: Introduction

Welcome to Assignment 1! In this assignment, you will be introduced to the fundamentals of **detection rule writing** (sometimes also called **detection engineering**), a key skill in modern cybersecurity. Detection engineering focuses on creating rules that allow security teams to **spot malicious activity early**, whether an attacker is actively operating in the environment or has already gained a foothold. Rather than reacting only after damage is done, well-designed detection rules help analysts **identify and respond to threats quickly and consistently**.

Detection rule writing is also closely tied to **Threat Intelligence**. Many real-world Indicators of Compromise (IoCs), such as file hashes, suspicious strings, and behavioural artifacts, can be translated into detection logic to help protect systems from future attacks and speed up triage during investigations.

In this assignment, we will focus on **YARA**, one of the most widely used rule languages for **malware detection**. YARA rules are commonly used by SOC teams and threat researchers to scan files and memory for known malicious patterns. In practice, YARA enables analysts to:

* Create **custom malware detections** for their environment
* Build **reusable, shareable rules** using a standard format
* Rapidly triage large numbers of samples by automatically flagging suspicious artifacts

There are many public rule collections available for learning and reference, such as this curated list of [YARA resources](https://github.com/InQuest/awesome-yara). By the end of this assignment, you should be comfortable reading and writing YARA rules, and applying them to real malware samples and memory artifacts.

<br>

### TLDR of YARA and How It Works

Essentially, **YARA is a pattern-matching tool commonly used to identify and classify files based on patterns found in their contents**.

Like everything stored on your computer, a file is ultimately made up of data represented as bytes. These bytes can be interpreted in many different ways. For example, as ASCII text, hexadecimal values, Unicode strings, or other data structures.

What YARA does is scan the contents of a file and look for patterns that you define in a **YARA rule**. These patterns can include:

* Text strings
* Hexadecimal byte sequences
* Regular expressions
* Combinations of multiple patterns and conditions

For example, suppose you want to search for the word `"Apple"` inside a file:

```yara
strings:
    $apple = "Apple"

condition:
    $apple
```

YARA will search the file for the bytes corresponding to the string `"Apple"`. If those bytes are present, the rule matches. Otherwise, it does not.

However, there is an important distinction between **what you see when opening a file** and **what is actually stored inside the file**.

For example, a PDF may visibly display the word **Apple**, but the literal string `"Apple"` may not actually appear anywhere in the file's raw contents. PDFs can compress, encode, split, or otherwise transform their internal data. In such cases, a simple YARA rule searching for `"Apple"` may not match.

This is why malware analysts may first inspect the actual contents of a binary (using tools such as `strings`, hex editors, disassemblers, or decompilers, which you will get to explore later in this assignment!) to identify useful patterns before writing a YARA rule.


<br>

---

<br>

## Part 2: YARA Rule Writing

YARA rule writing is essentially asking questions about a file: *Does it contain this text?* or *Does it contain these bytes?*

Feel free to use the provided `yara.exe` binary in this folder to run your rules against a file sample. If you are on Linux/macOS, you can install it with `apt` or `brew` as needed.

<br>

### Basics of YARA

A basic YARA rule has 4 main components:

```yara
rule RuleName {
    meta:
        author = "Your Name"
        description = "What this rule looks for"

    strings:
        $s1 = "some string"
        $s2 = "another string"

    condition:
        all of them
}
```

<br>

#### 1. Rule Name

```yara
rule RuleName {
```

Every YARA rule must start with the keyword `rule` followed by a **rule identifier**. In this example, the rule name is `RuleName`. 

The rule name should be **descriptive**, so that analysts can easily understand what it detects.

The rule name:

* Must **not start with a number**
* Must be **less than 128 characters**
* Must **not be a reserved keyword** (e.g., `rule`, `meta`, `condition`, `and`, `or`, `any`, `all`)

<br>

#### 2. `meta` Section (Rule Metadata Information)

```yara
meta:
    author = "Your Name"
    description = "What this rule looks for"
```

The `meta` section stores **human-readable information** about the rule.
This information is **not used for detection**, but is important for:

* Documentation
* Rule sharing
* Maintenance and version tracking

In this example:

* `author` tells us **who wrote the rule**
* `description` explains **what the rule detects**

Other common meta fields include:

* `version`
* `date`
* `reference`

<br>

#### 3. `strings` Section (What YARA Looks For)

```yara
strings:
    $s1 = "some string"
    $s2 = "another string"
```

The `strings` section defines the **patterns that YARA will search for** inside a file.
Each string:

* Starts with `$` (e.g. `$s1`, `$s2`, can be anything really)
* Has a **pattern to match**
* May include **modifiers** like `ascii`, `wide`, `nocase`, `fullword`

In this example:

* `$s1` looks for `"some string"`
* `$s2` looks for `"another string"`

These could represent:

* File names
* URLs
* Commands
* Malware strings
* Configuration values
* Raw bytes (E.g. file headers, process names, etc)

<br>

#### 4. `condition` Section (When the Rule Triggers)

```yara
condition:
    all of them
```

The `condition` section defines **the logic that decides when the rule matches**.
In this example:

* Both `$s1` and `$s2` must be present in the file for the rule to trigger.

Other common condition examples:

```yara
$s1                  // matches string $s1
$s1 or $s2           // matches string $s1 or $s2
any of them          // at least one string must match
1 of ($s*)           // at least one string starting with $s
filesize < 200KB     // file size restriction
```

Conditions can combine:

* Strings
* Bytes
* Logical operators (`and`, `or`, `not`)
* Iteration (`for` loops)

<br>

For more information on YARA rules and their specific nuances, the best place to look at is the [documentation](https://yara.readthedocs.io/en/latest/).

Let's try some examples!

<br>

#### Exercise 1 [1 Mark]

Q1. Write a YARA rule to detect if a file is UPX-packed [0.5 Mark]

```yara
rule is_upx_packed {
    strings: 
        $s1 = "<FILL IN THE BLANK>"
        $s2 = "<FILL IN THE BLANK>"
        $s3 = "<FILL IN THE BLANK>"
        $magic = "<FILL IN THE BLANK>"

    condition:
        <CONDITION 1> and <CONDITION 2>
}
```

<br>

Q2: Write a YARA rule to detect whether a file is a Windows Portable Executable (PE) [0.5 Mark]

*Hint*: You will need to use the `uint16()` and `uint32()` commands to read 2-byte and 4-byte addresses specifically.

```yara
rule is_pe {
    condition:
        // 1. Check for 'MZ' magic bytes at the very beginning (Offset 0)
        // YARA reads the 2-byte address in little-endian, so remember to reverse the byte order!
        <FILL IN CONDITION 1>

        and

        // 2. Check for 'PE\0\0' magic bytes at the address specified in the e_lfanew field
        // The e_lfanew field is always located at offset 0x3C (60) in the DOS header.
        // We read the 4-byte address at 0x3C (e_lfanew field), jump to that address, and check for 0x00004550 (PE\0\0)
        <FILL IN CONDITION 2>
}
```

<br>

---

<br>

### Writing practical YARA rules

Now that you have seen the basic structure of a YARA rule, let's try to do something more practical, by using YARA to detect a real piece of malware.

We will use a sample of **ZoxPNG RAT** (used by [APT17](https://cloud.google.com/blog/topics/threat-intelligence/hiding_in_plain_sight/)), which you will find in the `samples/` directory. Its extension has been changed from `.exe` to `.bin` so it will not run directly, but you should still exercise caution. If you want to experiment with it and run your YARA rule locally, do so inside a VM. Linux and macOS users are generally safer here, since this Windows malware will not run natively on those systems.

<br>

#### Step 1: Extracting interesting strings

Most YARA rules often rely on unique strings as patterns for detection. As such, let's try and extract some unique strings we can we use to recognise this binary.

We can use the `strings` command-line tool for that. On Linux/macOS you likely already have `strings`; on Windows, you can use the provided `strings.exe`.

What `strings` does is scan the raw bytes of a file and display sequences that correspond to printable text. Threat actors often need to hardcode certain information into their binaries (e.g. domain names, IP addresses, file paths, commands, or other configuration data). If this information is not properly obfuscated or encrypted, these strings can often be found quite easily using `strings`!


Example:

```bash
strings zoxpng.bin
```

You'll get a very long output, including normal PE artifacts, library names, error messages, and some very suspicious-looking content. For example:

```text
!This program cannot be run in DOS mode.
Rich
.text
`.rdata
@.data
---SNIP---
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
deflate 1.1.4 Copyright 1995-2002 Jean-loup Gailly

inflate 1.1.4 Copyright 1995-2002 Mark Adler
Sleep
LocalAlloc
CloseHandle
GetLastError
VirtualFree
VirtualAlloc
GetProcAddress
LoadLibraryA
GetCurrentProcessId
GlobalMemoryStatusEx
GetCurrentProcess
GetACP
GetVersionExA
GetComputerNameA
GetTickCount
GetSystemTime
LocalFree
CreateProcessA
CreatePipe
TerminateProcess
ReadFile
PeekNamedPipe
WriteFile
SetFilePointer
CreateFileA
GetFileSize
GetDiskFreeSpaceExA
GetDriveTypeA
GetLogicalDriveStringsA
CreateDirectoryA
FindClose
FindNextFileA
FindFirstFileA
MoveFileExA
OpenProcess
KERNEL32.dll
LookupAccountSidA
ADVAPI32.dll
SHFileOperationA
SHELL32.dll
strcpy
rand
sprintf
memcpy
strncpy
srand
_snprintf
atoi
strcat
strlen
printf
memset
strchr
memcmp
MSVCRT.dll
_exit
_XcptFilter
exit
__p___initenv
__getmainargs
_initterm
__setusermatherr
_adjust_fdiv
__p__commode
__p__fmode
__set_app_type
_except_handler3
_controlfp
InternetCrackUrlA
InternetCloseHandle
InternetReadFile
HttpQueryInfoA
HttpSendRequestA
InternetSetOptionA
HttpAddRequestHeadersA
HttpOpenRequestA
InternetConnectA
InternetOpenA
WININET.dll
ObtainUserAgentString
urlmon.dll
WTSFreeMemory
WTSEnumerateProcessesA
WTSAPI32.dll
GetModuleFileNameExA
PSAPI.DLL
calloc
free
http://%s/imgres?q=A380&hl=en-US&sa=X&biw=1440&bih=809&tbm=isus&tbnid=aLW4-J8Q1lmYBM:&imgrefurl=http://%s&docid=1bi0Ti1ZVr4bEM&imgurl=http://%s/%04d-%02d/%04d%02d%02d%02d%02d%02d.png&w=800&h=600&ei=CnJcUcSBL4rFkQX444HYCw&zoom=1&ved=1t:3588,r:1,s:0,i:92&iact=rc&dur=368&page=1&tbnh=184&tbnw=259&start=0&ndsp=20&tx=114&ty=58
http://0.0.0.0/1
http://0.0.0.0/2
Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NETCLR 2.0.50727)
image/pjpeg
image/jpeg
image/x-xbitmap
image/gif
Content-Type: application/x-www-form-urlencoded
B64:[%s]
Step 11
Step 10
Step 9
Step 8
Step 7
Step 6
Content-Type: image/x-png
Step 5
Step 4
Connection: close
Accept-Encoding: gzip, deflate
Accept-Language: en-US
Pragma: no-cache
User-Agent:
Cookie: SESSIONID=%s
Step 3
HTTP/1.1
Step 2
POST
Step 1
Get URL Info Error
[IISEND=0x%08X][Recv:] 0x%08X %s
IISCMD Error:%d
hWritePipe2 Error:%d
kernel32.dll
QueryFullProcessImageName
Not Support This Function!
1.1.4
need dictionary
incorrect data check
incorrect header check
invalid window size
unknown compression method
incompatible version
buffer error
insufficient memory
data error
stream error
file error
stream end
---SNIP---
```

From this, a few things immediately stand out:

1. **Suspicious User-Agent**

   ```text
   Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NETCLR 2.0.50727)
   ```

   This looks like a hard-coded User-Agent string for HTTP requests, that is strangely specific.

2. **Long URL with many parameters**

   ```text
   http://%s/imgres?q=A380&hl=en-US&sa=X&biw=1440&bih=809&tbm=isus&tbnid=aLW4-J8Q1lmYBM:&imgrefurl=http://%s&docid=1bi0Ti1ZVr4bEM&imgurl=http://%s/%04d-%02d/%04d%02d%02d%02d%02d%02d.png&...
   ```

   This looks like a template URL where `%s` will be filled in at runtime. It is very long and quite unlikely to appear in normal software. Strings like this are excellent detection candidates.

3. **Suspicious HTTP / C2-related strings**

   There are also several strings that appear to be used for constructing HTTP requests to exchange data with a remote server:

   ```text
   B64:[%s]                            // formatted Base64-encoded data
   Cookie: SESSIONID=%s                // use of HTTP cookies to track a session with a server
   Content-Type: image/x-png           // HTTP traffic presented as PNG image data
   Content-Type: application/x-www-form-urlencoded
   HTTP/1.1
   POST
   Connection: close
   Accept-Encoding: gzip, deflate
   ```

   Individually, strings such as `POST` or `HTTP/1.1` are very common and would make poor YARA strings. However, more unusual strings such as `B64:[%s]`, `Cookie: SESSIONID=%s`, and `Content-Type: image/x-png` are more interesting, especially when they appear together.

4. **Unusual hard-coded URLs**

   ```text
   http://0.0.0.0/1
   http://0.0.0.0/2
   ```

   These are unusual URLs to find hard-coded inside a normal application. They may be placeholders or internal values used by the malware, and can therefore be useful supporting detection strings.

5. **Contextual / internal strings**

   These may not be unique on their own, but together they may explain what the malware is trying to do:

   ```text
   Get URL Info Error                 // error message related to retrieving URL information
   IISCMD Error:%d                    // internal error message related to an IIS-like command
   [IISEND=0x%08X][Recv:] 0x%08X %s   // formatted debug/log string for sent and received data
   hWritePipe2 Error:%d               // error writing to a pipe (likely process I/O)
   Not Support This Function!         // fallback message for unsupported functionality
   ```

   These strings appear quite specific to the implementation of this particular binary.

6. **Step markers**

   We can also see a sequence of `Step` strings:

   ```text
   Step 1
   Step 2
   Step 3
   Step 4
   Step 5
   Step 6
   Step 7
   Step 8
   Step 9
   Step 10
   Step 11
   ```

   A single string such as `Step 1` would be too generic to use for detection. However, the presence of many of these strings together may be useful as supporting evidence when combined with stronger malware-specific strings.

We can infer that this binary is probably trying to communicate over HTTP and tunnel encoded data inside its requests, while making some of the traffic appear to be related to image content.

When selecting strings for a YARA rule, try to prioritise strings that are **specific to the malware's implementation**, rather than strings that simply indicate general functionality.

For example, these would be relatively strong candidates:

```text
B64:[%s]
Cookie: SESSIONID=%s
Content-Type: image/x-png
Get URL Info Error
IISCMD Error:%d
[IISEND=0x%08X][Recv:] 0x%08X %s
hWritePipe2 Error:%d
Not Support This Function!
http://0.0.0.0/1
http://0.0.0.0/2
imgres?q=A380&hl=en-US&sa=X&biw=1440&bih=809&tbm=isus&tbnid=aLW4-J8Q1lmYBM
tbm=isus&tbnid=aLW4-J8Q1lmYBM:&imgrefurl=http://%s&docid=1bi0Ti1ZVr4bEM&imgurl=http://%s
Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NETCLR 2.0.50727)
```

On the other hand, strings such as the following would generally be poor detection candidates on their own:

```text
!This program cannot be run in DOS mode.
KERNEL32.dll
MSVCRT.dll
HTTP/1.1
POST
strlen
memcpy
strcpy
sprintf
calloc
free
deflate 1.1.4
inflate 1.1.4
Symantec Corporation
Thawte Code Signing CA
```

These appear in many legitimate programs and would therefore be much more likely to cause false positives.

<br>

#### Step 2: Using imphash (import hash)

Besides strings, detection engineers often use the [**import hash**](https://cloud.google.com/blog/topics/threat-intelligence/tracking-malware-import-hashing/), or **imphash**, to track PE imports. An imphash is a hash calculated over a program's **import table** (the list of DLLs and functions it uses).

This is super useful because

* Malware authors may change file names or tweak some strings, but related samples often **continue using a similar set of imported APIs**.
* The imphash can therefore be relatively stable **across closely related malware samples**.
* It is also a good way to **cluster related samples** and write rules that survive minor changes in the malware's code or strings.

We have provided a small script `imphasher.py` that calculates the imphash for a file. Running it:

```bash
python3 imphasher.py zoxpng.bin
```

gives:

```text
414bbd566b700ea021cfae3ad8f4d9b9
```

We can use this value in our YARA rule through the `pe` module by including it in the condition section as follows:

```text
import "pe"

<SNIP>

condition:
    pe.imphash() == "414bbd566b700ea021cfae3ad8f4d9b9"
```

<br>

#### Step 3: Putting it all together in a YARA rule

Now we have three useful ingredients:

* A specific **imphash**
* A couple of **highly distinctive strings** (User-Agent and long URL)
* A group of **supporting strings** that describe behaviour

Here is a complete YARA rule that uses all of them:

```yara
import "pe"

rule is_zoxpng_rat {
    meta:
        author = "SC4016 Cyber Threat Intelligence"
        description = "Detects APT17 Malware (ZoxPNG RAT)"
        date = "20251212"
        reference = "https://intezer.com/blog/evidence-aurora-operation-still-active-part-2-more-ties-uncovered-between-ccleaner-hack-chinese-hackers"
        hash1 = "07f93e49c7015b68e2542fc591ad2b4a1bc01349f79d48db67c53938ad4b525d"
        hash2 = "0375b4216334c85a4b29441a3d37e61d7797c2e1cb94b14cf6292449fb25c7b2"
        hash3 = "20cd49fd0f244944a8f5ba1d7656af3026e67d170133c1b3546c8b2de38d4f27"

    strings:
        $x1 = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NETCLR 2.0.50727)"
        $x2 = "imgres?q=A380&hl=en-US&sa=X&biw=1440&bih=809&tbm=isus&tbnid=aLW4-J8Q1lmYBM"
        $x3 = "tbm=isus&tbnid=aLW4-J8Q1lmYBM:&imgrefurl=http://%s&docid=1bi0Ti1ZVr4bEM&imgurl=http://%s"

        $s1 = "http://0.0.0.0/1"
        $s2 = "http://0.0.0.0/2"

        $s3 = "Content-Type: image/x-png"
        $s4 = "Cookie: SESSIONID=%s"
        $s5 = "B64:[%s]"

        $s6 = "Get URL Info Error"
        $s7 = "IISCMD Error:%d"
        $s8 = "[IISEND=0x%08X][Recv:] 0x%08X %s"
        $s9 = "hWritePipe2 Error:%d"
        $s10 = "Not Support This Function!"

    condition:
        (
            pe.imphash() == "414bbd566b700ea021cfae3ad8f4d9b9" or
            1 of ($x*) or
            7 of them
        )
}
```

Using a text editor of your choice (e.g. `nano`, `vim`, `VS Code`), copy and paste the rule above into a new file and save it as `zoxpng.yar`.

When writing a YARA rule, we usually include metadata so that future users can understand what the rule does and how it was created. Common fields include an `author` (who wrote the rule), a short `description` (what the rule detects), a `date` (when the rule was created or last updated), and a `reference` (the sources used to design the rule). We may also include known malware hashes such as `hash1`, `hash2`, and `hash3`, which represent verified samples of the same malware family used to validate and test the accuracy of the rule.

Notice how we split the strings into two groups:

* `$x1`-`$x3` are **very specific** to this malware sample. If a file contains even one of these, it is already highly suspicious.
* `$s1`-`$s10` are **behavioural strings**. Each one alone could still potentially appear in other software, but seeing many of them together is more indicative of this malware sample.

The condition reflects this logic:

* `pe.imphash() == "414bbd..."`
  If the imphash matches exactly, we are confident enough to trigger.
* `1 of ($x*)`
  If at least one of the very distinctive strings is present, it is also strong enough.
* `7 of them`
  If enough strings from the whole set match, the combination becomes unlikely to be a coincidence. This reduces false positives while still catching slightly modified variants.

And that's it! We've just written a useful YARA rule that can effectively catch a real piece of malware. To test our rule, we can run `yara` directly from the terminal:

```bash
yara zoxpng.yar zoxpng.bin
```

If the rule matches, YARA will print the rule name and the file it matched:

```text
is_zoxpng_rat zoxpng.bin
```

This tells us that our rule `is_zoxpng_rat` successfully detected the sample `zoxpng.bin`. For more detailed output, we can add the `-s` flag. This shows exactly which strings matched and their offsets inside the file:

```bash
yara -s zoxpng.yar zoxpng.bin
```

Output with `-s` flag:

```text
is_zoxpng_rat zoxpng.bin
0x867c:$x1: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NETCLR 2.0.50727)
0x8422:$x2: imgres?q=A380&hl=en-US&sa=X&biw=1440&bih=809&tbm=isus&tbnid=aLW4-J8Q1lmYBM
0x844f:$x3: tbm=isus&tbnid=aLW4-J8Q1lmYBM:&imgrefurl=http://%s&docid=1bi0Ti1ZVr4bEM&imgurl=http://%s
0x857c:$s1: http://0.0.0.0/1
0x85fc:$s2: http://0.0.0.0/2
0x87a4:$s3: Content-Type: image/x-png
0x884c:$s4: Cookie: SESSIONID=%s
0x8760:$s5: B64:[%s]
0x8894:$s6: Get URL Info Error
0x88cc:$s7: IISCMD Error:%d
0x88a8:$s8: [IISEND=0x%08X][Recv:] 0x%08X %s
0x88e0:$s9: hWritePipe2 Error:%d
0x8924:$s10: Not Support This Function!
```

**Thinking Deeper**: How can we further improve this YARA rule so that it only matches executable binaries and not arbitrary files? Refer back to the simple `is_pe` rule you wrote in Q1, how could that same PE-file condition be integrated here to make this detection more precise?

> Note: For simplicity, please **do not** include the `is_pe` rule or its associated condition logic in any of your answers. For the following questions, focus more on writing the strings and conditions used to detect the malware. You are also not required to use any string modifiers (e.g. `ascii`, `nocase`, etc).

Now it's your turn: using the same thought process (extract strings, pick distinctive ones, etc), try crafting your own YARA rule for another sample!

<br>

#### Exercise 2 [7 Marks]

Q3. Write a YARA Rule that detects the [**Dharma**](https://malpedia.caad.fkie.fraunhofer.de/details/win.dharma) ransomware [1 Mark]

```yara
rule is_dharma_ransomware {
    meta:
        description = "Detects Dharma Ransomware"
    strings:
        // Fill in your strings here

    condition:
        // Fill in your conditions here

}
```

<br>

Q4. Write a YARA Rule that detects the [**RacoonStealer**](https://www.acronis.com/en/tru/posts/raccoon-stealer-a-popular-and-dangerous-threat/) infostealer. [2 Marks]

*Hint*: The ZIP file contains **two RaccoonStealer binaries** from the same malware family, but they differ slightly in how they are constructed. Can you identify the differences? Your YARA rule must be able to **detect both binaries**.


```yara
rule is_raccoon_stealer {
    meta:
        description = "Detects RaccoonStealer Infostealer"
    
    strings:
        // Fill in your strings here

    condition:
        // Fill in your conditions here
}
```

<br>

Q5. Write a YARA Rule that detects the **Neuron Service** used by the [**Turla Group**](https://attack.mitre.org/groups/G0010/) [2 Marks]

*Hint*: It appears that the Neuron Service is built using the `.NET` framework, which means we need to apply some basic `.NET` assembly reversing techniques. Try running the [`monodis`](https://www.mono-project.com/docs/tools+libraries/tools/monodis/) tool on the binary with the `--output=neuron.txt` flag enabled, and observe the output in the `neuron.txt` file! Don't use `imphash` for this one, there's a lot of useful strings that can be detected!

```yara
rule is_neuron_service {
    meta:
        description = "Detects NeuronService by Turla Group"
    
    strings:
        // Fill in your strings here

    condition:
        // Fill in your conditions here
}
```

<br>

Q6. Write a YARA rule that detects this unknown malware (I wonder what it does? Try and figure it out!) [2 Marks]

*Hint*: Aidan wrote the malware, but being the lousy malware author he is, he forgot to strip any identifying information from it...

```yara
rule is_unknown_malware {
    meta:
        description = "Detects SC4016 Unknown Malware"
    
    strings:
        // Fill in your strings here

    condition:
        // Fill in your conditions here
}
```

<br>

---

<br>

### Advanced YARA: Investigation of the WannaCry Ransomware

Now, let's shift our focus to the Threat Intelligence side of detection. In this part, we are going to focus on how we can extract IoCs and use them to build stronger detection rules. To uncover useful IoCs, we often rely on basic digital forensics to understand what happened during an attack, how the malware behaved, and what artifacts it left behind.

In this section, your task is to extract meaningful IoCs from a system compromised by the WannaCry ransomware outbreak of 2017, which affected hundreds of thousands of systems worldwide. Inside the `samples/` directory, you are provided with a memory image of an infected system as well as a WannaCry malware sample. Using these materials, work through the questions below to explore how Threat Intelligence Analysts conduct investigations to uncover actionable threat information.

<br>

#### WannaCry Exercise 1 [1 Mark]

Q7. Extract useful strings from the WannaCry binary, and write a YARA Rule to detect the presence of these string artifacts in memory. [1 Mark]

*Hints*:
WannaCry exhibits several well-known behaviours that you can use as strong detection indicators:

* **Dropped binaries:**
  WannaCry does not operate as a single file, it drops **multiple executables** onto the infected system.

* **Kill-switch domain:**
  WannaCry contains a kill-switch mechanism. It attempts to connect to a specific **unregistered domain**.

  * If the connection fails, the ransomware encrypts the system.
  * If the connection succeeds, the malware stops execution.
  * The person who figured this out is actually a very well-known threat intelligence analyst / security researcher: [Marcus Hutchins](https://www.linkedin.com/in/malwaretech/)

* **Ransom note files:**
  Since WannaCry is a ransomware, it drops ransom note messages in multiple languages, using a **distinct file extension**.

* **Global mutex:**
  WannaCry creates a **global mutex** to prevent the same machine from being infected multiple times.

```yara
rule is_wannacry_artifacts {
    meta:
        description = "Identify WannaCry Memory Artifacts"
    
    strings:
        // Fill in your strings here

    condition:
        all of them
}
```

<br>

#### Using the Volatility Framework

The [Volatility Framework](https://github.com/volatilityfoundation/volatility3) is a widely used open-source memory forensics tool for analysing memory images across different operating systems. We can use the Volatility command-line tool (`vol.py`) on the provided memory image to list all processes that were running on the infected system via the `pslist` plugin as shown:

```bash
python3 vol.py -f infected_system.raw windows.pslist
```

which gives the output:

```text
Volatility 3 Framework 2.27.0
Progress:  100.00  PDB scanning finished                        
PID PPID ImageFileName Offset(V) Threads Handles  SessionId Wow64 CreateTime ExitTime File output

<SNIPPED>
```

From this output, important fields to focus on include:

* **PID (Process ID)** – the unique identifier for each running process
* **PPID (Parent Process ID)** – the PID of the process that spawned this process
* **ImageFileName** – the name of the executable that created the process
* **CreateTime** – when the process was started
* **ExitTime** – when the process terminated (if applicable)

By comparing the **PID and PPID values**, we can usually reconstruct **process relationships** (which process launched which), which is extremely useful for identifying:

* Suspicious process chains
* Malware execution paths
* Living-off-the-land behaviour (E.g. the malware process launching `cmd.exe`, etc)

YARA can also be integrated into Volatility via the `yarascan` plugin, which allows YARA rules or individual strings to be applied directly to memory analysis. To search the memory image for the presence of a specific string, use:

```bash
python3 vol.py -f infected_system.raw windows.vadyarascan.VadYaraScan --yara-string <STRING> --wide
```

For more information on the list of available Volatility plugins, you may refer to this simple [cheatsheet](https://blog.onfvp.com/post/volatility-cheatsheet/). *Hint*: This resource will be useful for the exercise below.

<br>

#### WannaCry Exercise 2 [3 Marks]

Q8. Study this [article](https://blogs.vmware.com/security/2022/09/threat-report-illuminating-volume-shadow-deletion.html), which explains how WannaCry performs shadow volume deletion. Using `yarascan`, identify the **exact name** of the process responsible for deleting shadow copies. [0.75 Mark]

```text
<PUT PROCESS NAME HERE>
```

<br>

Q9. For the process identified above in Q8., use the `pslist` plugin to determine its `PID`, `PPID`, and the name of the parent executable that spawned it (`ImageFileName`). [0.75 Mark]

```text
<PID>, <PPID>, <Parent ImageFileName>
```

<br>

Q10. In a previous exercise, the hint mentioned that WannaCry drops multiple executables onto the infected system. Search online to identify the Volatility plugin used for scanning files from memory, then use it to determine the unique parent folder name where these executables were dropped. Report only the **folder name**, not the full path. [0.75 Mark]

```text
<UNIQUE FOLDER NAME>
```

<br>

Q11. WannaCry is a type of ransomware that generates a unique RSA-2048 private key pair for each infected system and stores it on the local disk. Search online to identify the Volatility plugin used for examining open file handles, then use it to determine the name and location of the `.eky` file that stores the encrypted private key. Report the **complete file path** exactly as shown. [0.75 Mark]

```text
<FULL FILE PATH>
```

<br>

#### Memdumps with Volatility

In some cases, we may want to investigate a **specific process** in greater detail, especially if it appears suspicious. To do this, we can create a **targeted memory dump of just that process** and analyse what it was executing on the system.

Using Volatility, we can dump a specific process from memory using the `memmap` plugin with the following command:

```bash
python3 vol.py -f infected_system.raw windows.memmap --pid <PID> --dump
```

which produces a file named:

```text
pid.<PID>.dmp
```

This memory dump contains the raw memory pages used by the process. We can then analyse it using tools like the `strings` command to extract readable content such as:

* Executed commands
* Network destinations
* Dropped file names
* Embedded configuration values

<br>

#### WannaCry Exercise 3 [3 Marks]

Q12. Perform a memory dump of the **parent process** identified in Q9. Using the resulting dump file, determine the **exact command** that this parent process used to spawn the child process identified in Q8. [0.75 Mark]

*Hint:* The dump file is large and contains mostly noise, think of smart way to search for long commands while limiting output!

```text
<FULL COMMAND HERE>
```

<br>

Q13. Using the same memory dump from Q12, identify which **Windows services were intentionally terminated** by this parent process to avoid detection or disruption. Provide **all full commands** used to kill these services, list each command on a new line. [0.75 Mark]

```text
<FULL COMMAND 1>
<FULL COMMAND 2>
...
```

<br>

Q14. Perform a memory dump of the **child process** identified in Q8. From this dump, extract **all TOR browser domains** that the process attempts to connect to. List each domain on a new line. [0.75 Mark]

```text
<FULL DOMAIN 1>
<FULL DOMAIN 2>
...
```

<br>

Q15. Using the same memory dump from Q14, extract **all Bitcoin wallet addresses** that the process attempts to communicate with. List each address on a new line. [0.75 Mark]

*Hint:* These wallets use the **Legacy P2PKH Bitcoin address format**.

```text
<FULL ADDRESS 1>
<FULL ADDRESS 2>
...
```

## Part 3: Conclusion

In this assignment, you learned how to think like a detection engineer by translating threat intelligence and malware analysis into **practical YARA rules**. You covered the essentials of YARA structure (metadata, strings, and conditions), wrote rules for common traits like **packers** and **PE file identification**, and then applied the same methodology to real malware samples by selecting distinctive indicators (high-signal strings, behavioural artifacts, and **imphash**).

You also took a more investigation-driven approach using the WannaCry memory image, where you practiced extracting meaningful IoCs from **memory forensics** (Volatility + YARA scanning), reconstructing suspicious process activity, and identifying artifacts such as dropped executables, commands, and attacker infrastructure indicators.

Lastly, you have learnt that strong YARA rules are not just "string matching" rules, they achieve precision by combining multiple indicators, limiting scope (e.g. only PE files), and using conditions that remain effective even when malware changes slightly.

To improve your rules going forward, always test for:

* **False positives** (does it match clean files?)
* **False negatives** (does it still match variants?)
* **Scope control** (file type checks, size limits, and smarter conditions)

Good detections are repeatable, explainable, and maintainable!

​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
