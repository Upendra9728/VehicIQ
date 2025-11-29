import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(VehicIQApp());

class VehicIQApp extends StatelessWidget {
  const VehicIQApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VehicIQ',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: VehicleForm(),
    );
  }
}

class VehicleForm extends StatefulWidget {
  const VehicleForm({super.key});

  @override
  _VehicleFormState createState() => _VehicleFormState();
}

class _VehicleFormState extends State<VehicleForm> {
  File? _image;
  final picker = ImagePicker();
  final _numberController = TextEditingController();
  final _ownerController = TextEditingController();
  bool _uploading = false;

  Future<void> _getImage(ImageSource source) async {
    final pickedFile = await picker.pickImage(source: source);
    setState(() {
      if (pickedFile != null) {
        _image = File(pickedFile.path);
      }
    });
  }

  Future<void> _uploadData() async {
    if (_image == null ||
        _numberController.text.isEmpty ||
        _ownerController.text.isEmpty) return;

    setState(() {
      _uploading = true;
    });

    var uri = Uri.parse('https://vehiciq-1.onrender.com/upload/');

    var request = http.MultipartRequest('POST', uri)
      ..fields['number'] = _numberController.text
      ..fields['owner'] = _ownerController.text
      ..files.add(await http.MultipartFile.fromPath('image', _image!.path));

    var response = await request.send();

    setState(() {
      _uploading = false;
    });

    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Upload successful!')));
    } else {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Upload failed!')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('VehicIQ')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            TextField(
              controller: _numberController,
              decoration: InputDecoration(labelText: 'Vehicle Number'),
            ),
            TextField(
              controller: _ownerController,
              decoration: InputDecoration(labelText: 'Owner Name'),
            ),
            SizedBox(height: 16),
            _image == null
                ? Text('No image selected.')
                : Image.file(_image!, height: 200),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  icon: Icon(Icons.camera_alt),
                  label: Text('Camera'),
                  onPressed: () => _getImage(ImageSource.camera),
                ),
                ElevatedButton.icon(
                  icon: Icon(Icons.photo),
                  label: Text('Gallery'),
                  onPressed: () => _getImage(ImageSource.gallery),
                ),
              ],
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _uploading ? null : _uploadData,
              child: _uploading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('Upload'),
            ),
            SizedBox(height: 32),
            ElevatedButton(
              child: Text('View Vehicles'),
              onPressed: () {
                Navigator.push(context,
                    MaterialPageRoute(builder: (context) => VehicleList()));
              },
            ),
          ],
        ),
      ),
    );
  }
}

class VehicleList extends StatefulWidget {
  const VehicleList({super.key});

  @override
  _VehicleListState createState() => _VehicleListState();
}

class _VehicleListState extends State<VehicleList> {
  List vehicles = [];
  bool loading = true;

  Future<void> fetchVehicles() async {
    var response = await http
        .get(Uri.parse('https://vehiciq-1.onrender.com/vehicles/'));

    if (response.statusCode == 200) {
      setState(() {
        vehicles = jsonDecode(response.body);
        loading = false;
      });
    } else {
      setState(() {
        loading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    fetchVehicles();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Vehicles')),
      body: loading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: vehicles.length,
              itemBuilder: (context, index) {
                var v = vehicles[index];
                return ListTile(
                  title: Text(v['number'] ?? ''),
                  subtitle: Text(v['owner'] ?? ''),
                  leading: v['image_path'] != null
                      ? Image.network(
                          'https://vehiciq-1.onrender.com/image/${v['id']}',
                          width: 50,
                          height: 50,
                          fit: BoxFit.cover,
                        )
                      : null,
                );
              },
            ),
    );
  }
}
