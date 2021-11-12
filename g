digraph structs {
	graph [rankdir=LR]
	node [fontname=Consolas rankdir=TB shape=Mrecord]
	"90e88581-03d1-45dd-9f0a-3442e4e55919" [label="{<90e88581-03d1-45dd-9f0a-3442e4e55919> Panel }|{ this is panel }"]
	"05e6a060-9c75-4316-b0a5-e40cd21ef2d3" [label="{<05e6a060-9c75-4316-b0a5-e40cd21ef2d3> Panel }|{ 3 }"]
	"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec" [label="{<cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec> Panel }|{ 2 }"]
	"2202ac55-5d77-4635-8b9f-c4dad5aa345d" [label="{<2202ac55-5d77-4635-8b9f-c4dad5aa345d> Panel }"]
	"1a071656-568c-430a-b32e-5ac6c3434843" [label="{<cdc601fb-42a7-4824-92e0-4b33e43b61bc> A |<b8983a60-69b8-4aef-843e-e9a210faae09> B }|{<1a071656-568c-430a-b32e-5ac6c3434843> A+B }|{<b6a4d1fa-dd12-46dc-8168-ba067f9a3bbb> Result }"]
	"6f3ef3b3-528a-4615-8ec3-7706e35e42c4" [label="{<90b19a55-358a-4c5e-9d83-65a4f42b730e> First Number |<6c3056b6-46c2-4dd8-8fae-964fe38a0196> Second Number }|{<6f3ef3b3-528a-4615-8ec3-7706e35e42c4> Larger }|{<15fdcf97-3430-4c02-8c8a-251a85b432d9> Larger than |<f9568371-ad48-43db-826f-37f8364744fc> … or Equal to }"]
	"f5a387f7-6abf-403c-bcb8-625be8f688c3" [label="{<f5a387f7-6abf-403c-bcb8-625be8f688c3> Panel }"]
	"38471e2d-36ae-491b-ad94-c15944b8ac48" [label="{<a207804b-3fea-4922-92cb-293ef6f65830> Input }|{<38471e2d-36ae-491b-ad94-c15944b8ac48> MA }|{<23e1ae8a-d87e-4bca-946b-03d9bbff15d1> Result |<4475a3a6-3cc4-489e-9b76-0cf418b6cd02> Partial Results }"]
	"51ccd63b-fb7a-4c45-93b3-967afb89d358" [label="{<ae4d896a-cda0-48c1-be41-2cde2a7cce29> range |<1d5db46e-f0a8-4fa1-8e52-fe1f97dd7b97> num |<398b44ec-dac5-41af-acc7-cee82abfcfb1> seed }|{<51ccd63b-fb7a-4c45-93b3-967afb89d358> CustomRandom }|{<dbc0282a-9d0d-4097-9182-40698477598b> out |<ca7016f1-b3ff-46eb-a1d3-52c50708869d> ret }"]
	"6f3ef3b3-528a-4615-8ec3-7706e35e42c4":"15fdcf97-3430-4c02-8c8a-251a85b432d9" -> "2202ac55-5d77-4635-8b9f-c4dad5aa345d":"2202ac55-5d77-4635-8b9f-c4dad5aa345d"
	"1a071656-568c-430a-b32e-5ac6c3434843":"b6a4d1fa-dd12-46dc-8168-ba067f9a3bbb" -> "2202ac55-5d77-4635-8b9f-c4dad5aa345d":"2202ac55-5d77-4635-8b9f-c4dad5aa345d"
	"05e6a060-9c75-4316-b0a5-e40cd21ef2d3":"05e6a060-9c75-4316-b0a5-e40cd21ef2d3" -> "1a071656-568c-430a-b32e-5ac6c3434843":"cdc601fb-42a7-4824-92e0-4b33e43b61bc"
	"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec":"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec" -> "1a071656-568c-430a-b32e-5ac6c3434843":"b8983a60-69b8-4aef-843e-e9a210faae09"
	"05e6a060-9c75-4316-b0a5-e40cd21ef2d3":"05e6a060-9c75-4316-b0a5-e40cd21ef2d3" -> "6f3ef3b3-528a-4615-8ec3-7706e35e42c4":"90b19a55-358a-4c5e-9d83-65a4f42b730e"
	"1a071656-568c-430a-b32e-5ac6c3434843":"b6a4d1fa-dd12-46dc-8168-ba067f9a3bbb" -> "f5a387f7-6abf-403c-bcb8-625be8f688c3":"f5a387f7-6abf-403c-bcb8-625be8f688c3"
	"05e6a060-9c75-4316-b0a5-e40cd21ef2d3":"05e6a060-9c75-4316-b0a5-e40cd21ef2d3" -> "38471e2d-36ae-491b-ad94-c15944b8ac48":"a207804b-3fea-4922-92cb-293ef6f65830"
	"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec":"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec" -> "38471e2d-36ae-491b-ad94-c15944b8ac48":"a207804b-3fea-4922-92cb-293ef6f65830"
	"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec":"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec" -> "51ccd63b-fb7a-4c45-93b3-967afb89d358":"1d5db46e-f0a8-4fa1-8e52-fe1f97dd7b97"
	subgraph group {
		color=lightgrey style=filled
		"90e88581-03d1-45dd-9f0a-3442e4e55919"
		"cbfb3127-7b1a-4723-8bf8-c8ae5a20e2ec"
	}
}
