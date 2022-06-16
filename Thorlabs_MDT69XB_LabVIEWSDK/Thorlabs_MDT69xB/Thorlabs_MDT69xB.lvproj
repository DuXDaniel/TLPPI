<?xml version='1.0' encoding='UTF-8'?>
<Project Name="Template - Generic.lvproj" Type="Project" LVVersion="11008008" URL="/&lt;instrlib&gt;/_Template - Generic/Template - Generic.lvproj">
	<Property Name="Instrument Driver" Type="Str">True</Property>
	<Property Name="NI.Project.Description" Type="Str">This project is used by developers to edit API and example files for LabVIEW Plug and Play instrument drivers.</Property>
	<Item Name="My Computer" Type="My Computer">
		<Property Name="CCSymbols" Type="Str">OS,Win;CPU,x86;</Property>
		<Property Name="NI.SortType" Type="Int">3</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="Examples" Type="Folder">
			<Item Name="Demo_Single-Channel device.vi" Type="VI" URL="/&lt;instrlib&gt;/Thorlabs_MDT69xB/Examples/Demo_Single-Channel device.vi"/>
			<Item Name="Demo_3 - Channel device_Main .vi" Type="VI" URL="/&lt;instrlib&gt;/Thorlabs_MDT69xB/Examples/Demo_3 - Channel device_Main .vi"/>
			<Item Name="Demo_3 - Channel device_SetXYZRange.vi" Type="VI" URL="/&lt;instrlib&gt;/Thorlabs_MDT69xB/Examples/Demo_3 - Channel device_SetXYZRange.vi"/>
		</Item>
		<Item Name="Data" Type="Folder">
			<Item Name="CmdLibrary.h" Type="Document" URL="/&lt;instrlib&gt;/Thorlabs_MDT69xB/Data/CmdLibrary.h"/>
			<Item Name="MDT_COMMAND_LIB_win32.dll" Type="Document" URL="/&lt;instrlib&gt;/Thorlabs_MDT69xB/Data/MDT_COMMAND_LIB_win32.dll"/>
			<Item Name="MDT_COMMAND_LIB_x64.dll" Type="Document" URL="/&lt;instrlib&gt;/Thorlabs_MDT69xB/Data/MDT_COMMAND_LIB_x64.dll"/>
		</Item>
		<Item Name="Thorlabs_MDT69xB.lvlib" Type="Library" URL="/&lt;instrlib&gt;/Thorlabs_MDT69xB/Thorlabs_MDT69xB.lvlib"/>
		<Item Name="Dependencies" Type="Dependencies">
			<Item Name="vi.lib" Type="Folder">
				<Item Name="subTimeDelay.vi" Type="VI" URL="/&lt;vilib&gt;/express/express execution control/TimeDelayBlock.llb/subTimeDelay.vi"/>
			</Item>
		</Item>
		<Item Name="Build Specifications" Type="Build">
			<Item Name="My Zip File" Type="Zip File">
				<Property Name="Absolute[0]" Type="Bool">true</Property>
				<Property Name="BuildName" Type="Str">My Zip File</Property>
				<Property Name="Comments" Type="Str"></Property>
				<Property Name="DestinationID[0]" Type="Str">{76032235-0A51-4B7F-A004-8A5FF888A57E}</Property>
				<Property Name="DestinationItemCount" Type="Int">1</Property>
				<Property Name="DestinationName[0]" Type="Str">Destination Directory</Property>
				<Property Name="IncludedItemCount" Type="Int">1</Property>
				<Property Name="IncludedItems[0]" Type="Ref">/My Computer</Property>
				<Property Name="IncludeProject" Type="Bool">true</Property>
				<Property Name="Path[0]" Type="Path">/E/SharedFolder/MDT69XB LabVIEW Instrument Driver.zip</Property>
				<Property Name="ZipBase" Type="Str">NI_zipbasedefault</Property>
			</Item>
		</Item>
	</Item>
</Project>
