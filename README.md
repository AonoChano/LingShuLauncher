
# LingShu Launcher

[中文README](ReadME-zhcn.md)

## Introduction
LingShu Launcher is an application launcher inspired by the concept of "LingShu" in Chinese culture, aiming to be a flexible and key tool for users to manage and launch programs easily. It allows you to add, delete, and arrange programs in a grid layout, providing a convenient way to access your frequently - used applications.

## Features
- **Program Management**: Add and delete programs with ease. You can quickly include new applications or remove those you no longer need.
- **Grid Layout**: Programs are presented in an organized grid layout. The layout automatically adjusts based on the number of programs, ensuring a clean and accessible interface.
- **Icon Display**: Each program is represented by its corresponding icon (if available). For files without proper icons, a default label is shown.
- **Configuration Saving**: The launcher saves your program configurations, including the list of added programs and layout mode settings, to a JSON file. This ensures that your personalized setup is retained across sessions.

## Known Issues
- **URL Icon Import Problem**: There is an issue with importing URL - based icons. For example, the desktop icon created by Steam cannot be imported and displayed correctly.
- **Right - click Drag Function Defect**: The right - click drag - and - drop functionality for reordering programs has some glitches, which may affect the smoothness of arranging programs.

## Installation
1. Ensure you have Python installed on your system. If not, download and install it from the official Python website.
2. Install the required libraries. Open your command prompt or terminal and run the following commands:
```bash
pip install PyQt5 pywin32
```
3. Clone the project repository to your local machine:
```bash
git clone [repository_url]
```
4. Navigate to the project directory:
```bash
cd [project_directory]
```

## Usage
1. Run the `launch.py` file:
```bash
python launch.py
```
2. **Adding Programs**: Click the "➕" button in the launcher. A file dialog will open, allowing you to select the executable file (`.exe`) of the program you want to add.
3. **Deleting Programs**: In layout mode (enabled by checking the "布局模式" checkbox), click the middle mouse button on a program icon to delete it.
4. **Reordering Programs**: In layout mode, right - click on a program icon to start the drag - and - drop operation for reordering. However, due to the existing issue, this functionality may not work perfectly.
5. **Launching Programs**: Left - click on a program icon to launch the corresponding application.

## List to Do
- **Fix URL Icon Import**: Resolve the problem of importing URL - based icons. This includes improving the detection and handling of icons for applications like Steam to ensure accurate and consistent icon display.
- **Enhance Right - click Drag Functionality**: Debug and improve the right - click drag - and - drop feature. Implement a more stable and user - friendly reordering mechanism to allow seamless arrangement of programs.
- **User Interface Optimization**: Improve the overall appearance of the launcher. This could involve adjusting the color scheme, icon sizes, and layout spacing for a more aesthetically pleasing and visually organized interface.
- **Add Program Categorization**: Implement a categorization system for programs. Users could group programs into different categories (e.g., Work, Entertainment, Utilities), making it even easier to find and manage applications.
- **Cross - Platform Compatibility**: Currently developed for Windows, explore the possibility of making the launcher cross - platform, supporting operating systems like macOS and Linux.

## Sponsorship
If you find LingShu Launcher useful and would like to support its development, you can contribute through the following payment methods:

<table>
  <tr>
    <td><img src="WeChatPay.png" alt="WeChat Pay" width="200"></td>
    <td><img src="Alipay.png" alt="Alipay" width="200"></td>
  </tr>
</table>

## License
This project is licensed under the [Your License Name] license. See the `LICENSE` file for more details.
