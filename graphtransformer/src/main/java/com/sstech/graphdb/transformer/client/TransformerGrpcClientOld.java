//package com.sstech.graphdb.transformer.client;
//
//import com.sstech.graphdb.transformer.grpc.ServicesToGraphCoreClient;
//import com.sstech.graphdb.transformer.grpc.ServicesToGraphLoaderClient;
//import com.sstech.graphdb.transformer.utils.ConnectionProperties;
//import io.rsocket.RSocket;
//import io.rsocket.RSocketFactory;
//import io.rsocket.transport.netty.client.TcpClientTransport;
//
//public class TransformerGrpcClient {
//
//    public static void main(String[] args) {
//        RSocket loaderConnector =
//                RSocketFactory
//                    .connect()
//                    .transport(TcpClientTransport.create(ConnectionProperties.GRAPH_LOADER_PORT))
//                    .start()
//                .block();
//
//        RSocket coreConnector =
//                RSocketFactory
//                        .connect()
//                        .transport(TcpClientTransport.create(ConnectionProperties.GRAPH_CORE_PORT))
//                        .start()
//                        .block();
//
//        ServicesToGraphLoaderClient toGraphLoaderClient = new ServicesToGraphLoaderClient(loaderConnector);
//        ServicesToGraphCoreClient toGraphCoreClient = new ServicesToGraphCoreClient(coreConnector);
//    }
//}
