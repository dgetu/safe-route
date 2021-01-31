package com.example.saferoute;

import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.FragmentActivity;

import android.location.Address;
import android.location.Geocoder;
import android.os.Bundle;
import android.widget.SearchView;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

import java.io.IOException;
import java.util.List;

//imports for heat map
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import java.util.UUID;

/**
 * @author Ian Wong
 * @version 2020.1.31
 *
 *          Activity class that handles the activities of the app
 *
 *
 */
public class MainActivity extends FragmentActivity implements OnMapReadyCallback {
    /**
     * The default zoom value for the map
     */
    public static final float DEFAULT_ZOOM = 15;
    /**
     * The maximum allowed results in a search query
     */
    private static final int MAX_RESULTS = 1;

    GoogleMap map;
    SupportMapFragment mapFragment;
    SearchView searchView;

    // initializing a big query object
    BigQuery bigquery = BigQueryOptions.getDefaultInstance().getService();

    /**
     * Method that runs when the app first starts up
     * 
     * @param savedInstanceState idk, the state in which the app saves ??!?
     *
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        searchView = findViewById(R.id.sv_location);
        mapFragment = (SupportMapFragment) getSupportFragmentManager().findFragmentById(R.id.google_map);

        searchView.setOnQueryTextListener(new SearchView.OnQueryTextListener() {
            /**
             * What happens when someone searches something Finds the address/location and
             * marks it on the map
             *
             * @param query String that the user searched
             * @return false, thats it
             */
            @Override
            public boolean onQueryTextSubmit(String query) {
                String location = searchView.getQuery().toString();
                List<Address> addressList = null;

                if (location != null || !location.equals("")) {
                    Geocoder geocoder = new Geocoder(MainActivity.this);
                    try {
                        addressList = geocoder.getFromLocationName(location, MAX_RESULTS);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                    Address address = addressList.get(0);
                    LatLng latLng = new LatLng(address.getLatitude(), address.getLongitude());
                    map.addMarker(new MarkerOptions().position(latLng).title(location));
                    map.animateCamera(CameraUpdateFactory.newLatLngZoom(latLng, DEFAULT_ZOOM));
                }
                return false;
            }

            /**
             * idk what this does
             * 
             * @param newText the text change ??!?!
             * @return false, thats it
             */
            @Override
            public boolean onQueryTextChange(String newText) {
                return false;
            }
        });

        mapFragment.getMapAsync(this);
    }

    /**
     * Runs when the map first starts up, just centers it on dc
     * 
     * @param googleMap Map object that started up
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        map = googleMap;

        LatLng dc = new LatLng(38.9072, -77.0369);
        map.moveCamera(CameraUpdateFactory.newLatLng(dc));
        map.moveCamera(CameraUpdateFactory.zoomTo(DEFAULT_ZOOM));

    }

    private void addHeatMap() {
        List<LatLng> latLngs = null;

        // Get the data: latitude/longitude positions of police stations.
        try {
            latLngs = readItems( runQuery() );
        } catch (JSONException e) {
            Toast.makeText(context, "Problem reading list of locations.", Toast.LENGTH_LONG).show();
        }

        // Create a heat map tile provider, passing it the latlngs of the police
        // stations.
        HeatmapTileProvider provider = new HeatmapTileProvider.Builder().data(latLngs).build();

        // Add a tile overlay to the map, using the heat map tile provider.
        TileOverlay overlay = map.addTileOverlay(new TileOverlayOptions().tileProvider(provider));
    }

    private List<LatLng> readItems(@RawRes int resource) throws JSONException {
        List<LatLng> result = new ArrayList<>();
        InputStream inputStream = context.getResources().openRawResource(resource);
        String json = new Scanner(inputStream).useDelimiter("\\A").next();
        JSONArray array = new JSONArray(json);
        for (int i = 0; i < array.length(); i++) {
            JSONObject object = array.getJSONObject(i);
            double X = object.getDouble("X");
            double Y = object.getDouble("Y");
            result.add(new LatLng(X, Y));
        }
        return result;
    }

    private Job runQuery() {
        QueryJobConfiguration queryConfig = QueryJobConfiguration
                .newBuilder("SELECT X, Y " + "FROM 'ornate-veld-161301.crime_data_dc.data_2020' "
                        + "ORDER BY subject DESC LIMIT 1000")
                // Use standard SQL syntax for queries.
                // See: https://cloud.google.com/bigquery/sql-reference/
                .setUseLegacySql(false).build();

        // Create a job ID so that we can safely retry.
        JobId jobId = JobId.of(UUID.randomUUID().toString());
        Job queryJob = bigquery.create(JobInfo.newBuilder(queryConfig).setJobId(jobId).build());

        // Wait for the query to complete.
        queryJob = queryJob.waitFor();

        // Check for errors
        if (queryJob == null) {
            throw new RuntimeException("Job no longer exists");
        } else if (queryJob.getStatus().getError() != null) {
            // You can also look at queryJob.getStatus().getExecutionErrors() for all
            // errors, not just the latest one.
            throw new RuntimeException(queryJob.getStatus().getError().toString());
        }
        return queryJob;
    }

    

}