# A script that converts junos vSRX configs into a cloud init user data file. Were that file can be included as part of a CloudFormation template. Or, directly copy and pasted into the user data section at launch.



<ul>
Steps
* Download the py file called converter.py. 
* Copy or create a file containing the junos configuration.  Ensure that the file has no spaces at the end.  
* Run the converter 
* Enter the file name of the file to be converted, and teh file name it will be converted to.
* For AWS CloudFormation, ensure to include the entire Userdata and its string "UserData":{string}. 
</ul>
<ul>


## Disclaimer

The code provided on this GitHub repository is provided "as is" and without any warranty, express or implied. By using this code, you acknowledge and agree to the following terms:

1. No Liability: The author of this code shall not be held liable for any damages, including but not limited to direct, indirect, incidental, special, or consequential damages, arising out of the use or inability to use this code, even if the author has been advised of the possibility of such damages.

2. No Warranty: The author makes no representations or warranties of any kind concerning the code, including but not limited to its accuracy, completeness, reliability, suitability, or fitness for any particular purpose. The code is provided without any warranty whatsoever, whether express, implied, or statutory.

3. Use at Your Own Risk: The use of this code is solely at your own risk. It is your responsibility to ensure that the code meets your specific requirements and is compatible with your software and systems. The author disclaims any responsibility for any adverse effects that may arise from the use of this code.

4. No Support: The author is under no obligation to provide support, assistance, or maintenance for the code. Any assistance provided by the author is at their sole discretion and may be subject to separate terms and conditions.

5. Third-Party Content: This code may incorporate or rely upon third-party libraries, modules, or other components. The author does not guarantee the accuracy, reliability, or suitability of any third-party content used in this code and shall not be responsible for any damages resulting from the use of such content.

By using this code, you agree to release and hold harmless the author from any and all claims, demands, or actions arising out of or in connection with your use of the code. If you do not agree with these terms, you should not use the code.

Please note that this disclaimer does not exempt the author from any liability that cannot be excluded or limited under applicable law.



## Attribution

The code provided here for this script was started using chatgpt, However, needed heavy heavy modifications by me, so I will call it my own. " ;-) "