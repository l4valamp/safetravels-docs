
# Asset Naming

| Asset Type         | Prefix | Grouping | Name | Number |
| ------------------ | ------ | -------- | ---- | ------ |
| Master Material    | MM_    |          |      |        |
| Material Instances | MI_    |          |      |        |
| Textures           | T_     |          |      |        |
| Static Mesh        | SM_    |          |      |        |
**Grouping** is optional. For example, if you are naming a Diner asset, grouping should be Building and the name should be Diner. If you have multiple diners, you should include the number. your asset would likely be named:
SM_Building_Diner_02

# IMPORTING ASSETS 

When you are importing a singular or a selection of assets it is important to have these settings selected to avoid cluttering the content browser. 

When the import content menu shows up, select 'use pipeline defaults' to reset your selections. YOU ONLY NEED TO DO THIS ONCE PER WORKSPACE- once you change your settings, they will stay the same until you change them again. Whenever you move to a new desktop or workspace you should ensure these settings are checked again when importing. 
![[Pasted image 20260731105848.png]]
If you want to try and rename your asset before importing you can deselect "Use source name for asset" and type your asset name in "Asset Name" but this has lowkey never worked for me
[[Pasted image 20260731105108.png]]
![[Pasted image 20260731105008.png]]
DO NOT BUILD NANITE!!! DESELECT BUILD NANITE!!!! IDK WHY THIS IS AN AUTOMATIC SETTING!!! This setting converts your mesh to a billion tris to be rendered with nanite exclusively. More info on nanite below. Its cool i guess but it creates issues like the entire team asking questions like "why does my mesh look like that." The answer is nanite

In the Materials and Textures settings, uncheck Import Materials and Import Textures. Unless you have pre-existing textures applied to the model you are importing, default duplicate blank materials will be imported which creates a significant amount of content clutter.
![[Pasted image 20260731104853.png]]

**_Troubleshooting_**
If your mesh has modified/custom normals (assets such as foliage) make sure to deselect recompute normals. You may also want to deselect recompute tangents. Unreal will recalculate your mesh's normals if this is selected, overriding any custom changes.
![[Pasted image 20260731105247.png]]

**IMPORTANT: NANITE**
Nanite is a geometry rendering option that was added to unreal in 5.0. It is meant for cinematic quality high poly assets and allows for suuuper high resolution assets to be rendered basically at the same speed as assets using the traditional pipeline. It creates LODs itself and doesnt need normals or occlusion because its high resolution. 
We don't want to use this! We are using the traditional pipeline. Nanite will slow down our game. 
