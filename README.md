# Bouncing Ball

## Overview

This project is a **procedurally generated animation** of a bouncing ball interacting with an **impossible staircase**, inspired by **MC Escher’s "Ascending and Descending"** and the **Grand Staircase from Harry Potter**. The animation is fully scripted in **Python within Maya**, incorporating procedural modeling, dynamic materials, and custom lighting setups.

Key features include:

* **Procedural Staircase** – Fully scripted model inspired by Escher's impossible geometry.
* **Bouncing Ball Animation** – Implements squash & stretch for realistic motion.
* **Dynamic Portrait Textures** – Animated moving portraits, referencing Harry Potter's Grand Staircase.
* **Custom Lighting & Materials** – Procedural shading & emissive textures to enhance the scene.
* **Scripted Camera Setup** – Ensures the perfect illusion perspective is maintained.

This project balances **technical scripting with artistic composition**, creating a visually striking and algorithmically controlled scene.

## Demo Videos

Watch the full demo [here](https://youtu.be/Q9KEmYCoY3g).

![image](./Refs/BouncingBall.gif)

## How to run the Project

1. **Open the Script Editor in Maya** 
    - `Windows > General Editors > Script Editor`

2. **Open the Main Script**
    - In the Script Editor, go to `File > Open Script...`
    - Navigate to the `scripts/` directory in the submission folder and select `main.py`.

3. **Update the Script Path**
    - Inside the `main.py` script, update the `SCRIPT_DIR` variable to the full path where the `scripts/` directory is located on your machine. For example:
    ```
    SCRIPT_DIR = r"C:/Users/YourName/Desktop/Maya/scripts"
    ```

4. **Run the Script**
    - Select all lines in the Script Editor and press the `Play` button to execute the script. Alternatively, you can press `Ctrl+Enter` (Windows) or `Cmd+Enter` (Mac) to execute the script.

5. **Materials**
    - If the materials (e.g., marble stairs or ground tiles) do not load correctly:
        - Use the `.mb` files in the `textures/` directory to import pre-built materials.
        - Alternatively, manually recreate the materials using the provided texture files in the `marble/` and `tile-2/` folders.
        - Refer to [Notes on materials](#notes-on-materials) for more information.

## Notes on materials

The `.mb` files for prebuilt materials may work but could have texture path issues depending on your setup. This may prevent them from loading correctly in the project.

The source files have been included in the `textures/` directory and can be manually created using Maya's Hypershade.
- Use the Arnold Standard Surface material.
- Assign the provided texture maps to the appropriate inputs (e.g., base color, normal, metallic, roughness).

Alternatively, the two prebuilt materials were sourced from [Poliigon](https://www.poliigon.com/), which offers a [material converter](https://www.poliigon.com/maya) tool that can also be used to build the materials manually.

## References:
```
Autodesk, 2024. Maya 2024 Technical Documentation Python. [online] Available from: https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=__CommandsPython_index_html [Accessed 1 October 2024].
Escher, M. C., 1960. Ascending and Descending [Lithograph]. mcescher.com: The M.C. Escher Company.
Harry Potter and the Philosopher's Stone, 2001. [Film] Directed by Chris Columbus. USA: Warner Bros. Pictures.
Morimoto, A., 2023. Make your own moving portrait. www.timeout.com: TimeOut. Available from: https://www.timeout.com/tokyo/attractions/guide-to-warner-bros-studio-tour-tokyo-the-making-of-harry-potter [Accessed 22 October 2024].
Poliigon., Denali Polished Quartzite Stone Texture, Gray. Available from: https://www.poliigon.com/texture/denali-polished-quartzite-stone-texture-gray/8060#license-info [Accessed 11 November 2024].
Poliigon., Square Slate Raw Tile Texture, Black. Available from: https://www.poliigon.com/texture/square-slate-raw-tile-texture-black/7657 [Accessed 11 November 2024].
saragnzalez, Brick wall texture. Freepik. Available from: https://www.freepik.com/free-photo/brick-wall-texture_1237699.htm [Accessed 11 November 2024].
Wizarding World Digital., 2017. The Hogwarts ghosts. Available from: https://www.harrypotter.com/features/hogwarts-ghosts [Accessed 22 October 2024].
Wizarding World Digital., 2017. The stories of the Hogwarts founders. Available from: https://www.harrypotter.com/features/stories-of-the-hogwarts-founders [Accessed 22 October 2024].
Wizarding World Digital., 2019. How do magical portraits actually work?. Available from: https://www.harrypotter.com/features/how-do-magical-portraits-actually-work [Accessed 22 October 2024].
```